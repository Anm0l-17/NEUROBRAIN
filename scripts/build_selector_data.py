"""Build citation-selector training, development and sealed evaluation rows.

Each row mirrors the app's real Ollama request (`extract.selection_payload`): a
question plus one to five evidence lines with 32-hex citation IDs, and the target
`{"citations": [...]}`, which is empty when no line answers the question.

Sources (downloaded by hand into .neurobrain/raw, hashes pinned below):
  SQuAD 2.0 (CC BY-SA 4.0), HotpotQA distractor (CC BY-SA 4.0): train + dev + eval
  LongMemEval oracle (MIT): sealed evaluation only
  Our fictional demo fixtures: sealed evaluation only

Run: python scripts/build_selector_data.py  (needs pyarrow)
"""

import hashlib
import json
import random
import re
import sys
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from neurobrain.extract import SELECT_SYSTEM  # noqa: E402

RAW = ROOT / ".neurobrain/raw"
OUT = ROOT / "data/selector_v1"
HASHES = {
    "squad_train.parquet": "f6da32ffb482ff463ad056477740d1bb284b96a45db3a08bee6a225ca6abf291",
    "squad_val.parquet": "0560174ab095c5ac0a8c8dc8da05f1625453c45a77e4ce9cabc6947ddfdd24cb",
    "hotpot_train0.parquet": "76d3bb3048a7cc73c1958107c0c5872a00d7e7d00c105b81e92f6769e7822e68",
    "hotpot_val.parquet": "c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6",
    "lme_oracle.json": "821a2034d219ab45846873dd14c14f12cfe7776e73527a483f9dac095d38620c",
}
MAX_LINE = 400
STOP = set(
    "a an the of to in on at for and or is are was were be by with as from that this "
    "what which who whom whose when where why how did do does it its his her their".split()
)
SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP}


def overlap(question, line):
    return len(words(question) & words(line))


def sentences(text):
    """Sentences with their character spans in `text`."""
    out, start = [], 0
    for part in SPLIT.split(text):
        begin = text.index(part, start)
        out.append((part, begin, begin + len(part)))
        start = begin + len(part)
    return out


def cite(rng):
    return f"{rng.getrandbits(128):032x}:{rng.randint(1, 40)}"


def row(rng, source, question, lines, gold):
    """lines: 5 texts, closest distractors first; gold: indexes that answer.

    The app's search returns 1 to 5 lines, so keep every gold line plus the closest
    distractors up to a random count in that range, then shuffle and assign citations.
    """
    assert len(lines) == 5 and len(set(lines)) == 5
    keep = rng.randint(max(1, len(gold)), 5)
    extra = [i for i in range(5) if i not in gold][: keep - len(gold)]
    order = sorted(gold) + extra
    rng.shuffle(order)
    evidence = [{"citation": cite(rng), "text": lines[i]} for i in order]
    target = [e["citation"] for e, i in zip(evidence, order) if i in gold]
    user = json.dumps({"question": question, "evidence": evidence})
    return {
        "source": source,
        "question": question,
        "evidence": evidence,
        "target": target,
        "messages": [
            {"role": "system", "content": SELECT_SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": json.dumps({"citations": target})},
        ],
    }


def closest(question, pool, k, exclude=()):
    ranked = sorted(
        (s for s in pool if s not in exclude and len(s) <= MAX_LINE),
        key=lambda s: -overlap(question, s),
    )
    return list(dict.fromkeys(ranked))[:k]


def squad(rng, path, titles=None):
    """Yield (title, kind, row) for SQuAD 2.0. kind: answer | unanswerable | removed."""
    for r in pq.read_table(path).to_pylist():
        if titles is not None and r["title"] not in titles:
            continue
        sents = sentences(r["context"])
        texts = [s for s, _, _ in sents]
        q = r["question"]
        answers = r["answers"]
        if not answers["text"]:
            lines = closest(q, texts, 5)
            if len(lines) == 5:
                yield r["title"], "unanswerable", row(rng, "squad2", q, lines, set())
            continue
        a_text, a_start = answers["text"][0], answers["answer_start"][0]
        hit = [s for s, b, e in sents if b <= a_start and a_start + len(a_text) <= e]
        if len(hit) != 1 or len(hit[0]) > MAX_LINE:
            continue
        others = [s for s in closest(q, texts, 6, exclude=hit) if a_text not in s]
        if len(others) >= 4 and rng.random() < 0.75:
            yield r["title"], "answer", row(rng, "squad2", q, hit + others[:4], {0})
        elif len(others) >= 5:
            # The answering sentence is removed: a same-topic near miss.
            yield r["title"], "removed", row(rng, "squad2", q, others[:5], set())


def hotpot(rng, path, limit):
    rows = pq.read_table(
        path, columns=["question", "answer", "supporting_facts", "context"]
    ).to_pylist()
    rng.shuffle(rows)
    made = 0
    for r in rows:
        ctx = dict(zip(r["context"]["title"], r["context"]["sentences"]))
        gold = []
        for t, i in zip(r["supporting_facts"]["title"], r["supporting_facts"]["sent_id"]):
            if t in ctx and i < len(ctx[t]):
                gold.append(ctx[t][i].strip())
        gold = list(dict.fromkeys(gold))
        pool = [s.strip() for sents in ctx.values() for s in sents if s.strip()]
        if not 2 <= len(gold) <= 3 or any(len(g) > MAX_LINE for g in gold):
            continue
        q, ans = r["question"], r["answer"]
        others = [s for s in closest(q, pool, 8, exclude=gold) if ans not in s]
        if rng.random() < 0.2 and len(others) >= 5 and ans not in ("yes", "no"):
            yield "removed", row(rng, "hotpotqa", q, others[:5], set())
        elif len(others) >= 5 - len(gold):
            lines = gold + others[: 5 - len(gold)]
            yield "answer", row(rng, "hotpotqa", q, lines, set(range(len(gold))))
        else:
            continue
        made += 1
        if made >= limit:
            return


def longmemeval(rng, path, limit):
    data = json.load(open(path))
    rng.shuffle(data)
    made = 0
    for x in data:
        abstain = x["question_id"].endswith("_abs")
        if not abstain and x["question_type"] not in ("single-session-user", "multi-session"):
            continue
        turns = [t for s in x["haystack_sessions"] for t in s if t["role"] == "user"]
        gold = list(dict.fromkeys(t["content"].strip() for t in turns if t.get("has_answer")))
        if not 1 <= len(gold) <= 3 or any(len(g) > 600 for g in gold):
            continue
        pool = [t["content"].strip() for t in turns if len(t["content"]) <= 600]
        others = closest(x["question"], pool, 5, exclude=gold)
        if len(others) < 5 - len(gold):
            continue
        lines = gold + others[: 5 - len(gold)]
        # Abstention questions point at a related fact that does not answer them.
        yield row(rng, "longmemeval", x["question"], lines, set() if abstain else set(range(len(gold))))
        made += 1
        if made >= limit:
            return


SAFFRON = [
    "The Saffron Bridge project kickoff is on 3 December 2026 in Room 4B.",
    "We decided to use PostgreSQL instead of MongoDB for the Saffron Bridge backend.",
    "Every Saffron Bridge API response must include a request ID.",
    "Priya prefers short bullet-point summaries over long reports.",
    "The Saffron Bridge budget review is still unresolved because the vendor quote has not arrived.",
    "The Saffron Bridge beta release is planned for 15 January 2027.",
    "Rohan will own the Saffron Bridge testing plan.",
]
DEMO = [
    "The violet demonstration is on 24 November 2026.",
    "The amber lighthouse audit for project Wren is on 9 December 2026.",
    "Mira prefers concise answers.",
    "The teal harbour review for project Kestrel is on 2 December 2026.",
]
FIXTURES = [
    ("When is the Saffron Bridge launch party?", SAFFRON[1:6], set()),
    ("When is the Saffron Bridge launch party?", SAFFRON[:5], set()),
    ("What must every Saffron Bridge API response include?", SAFFRON[:5], {2}),
    ("When is the Saffron Bridge kickoff?", SAFFRON[:5], {0}),
    ("Which database did we choose for the Saffron Bridge backend?", SAFFRON[1:6], {0}),
    ("How does Priya like summaries?", SAFFRON[2:7], {1}),
    ("Who owns the Saffron Bridge testing plan?", SAFFRON[2:7], {4}),
    ("When is the Saffron Bridge beta release?", SAFFRON[2:7], {3}),
    ("Who approved the Saffron Bridge budget?", SAFFRON[:5], set()),
    ("When is the pink submarine launch?", DEMO + SAFFRON[:1], set()),
    ("When is the violet demonstration?", DEMO + SAFFRON[:1], {0}),
    ("When is the amber lighthouse audit?", DEMO + SAFFRON[:1], {1}),
    ("When is the amber lighthouse party?", DEMO + SAFFRON[:1], set()),
    ("How does Mira like answers?", DEMO + SAFFRON[:1], {2}),
    ("Where is the teal harbour review held?", DEMO + SAFFRON[:1], set()),
]


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode()
    (OUT / name).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def main():
    for name, digest in HASHES.items():
        got = hashlib.sha256((RAW / name).read_bytes()).hexdigest()
        assert got == digest, f"{name} hash mismatch"
    rng = random.Random(17)

    titles = sorted({r["title"] for r in pq.read_table(RAW / "squad_train.parquet", columns=["title"]).to_pylist()})
    rng.shuffle(titles)
    dev_titles = set(titles[: len(titles) // 10])  # grouped by article: no shared paragraphs
    train_titles = set(titles) - dev_titles

    def take(stream, quota):
        got = {k: [] for k in quota}
        for _, kind, r in stream:
            if len(got[kind]) < quota[kind]:
                got[kind].append(r)
            if all(len(got[k]) >= quota[k] for k in quota):
                break
        return [r for k in quota for r in got[k]]

    squad_q = {"answer": 750, "unanswerable": 500, "removed": 300}
    train = take(squad(rng, RAW / "squad_train.parquet", train_titles), squad_q)
    hp = list(hotpot(rng, RAW / "hotpot_train0.parquet", 1600))
    dev_hp = hp[1450:]
    train += [r for _, r in hp[:1450]]
    dev = take(squad(rng, RAW / "squad_train.parquet", dev_titles), {"answer": 60, "unanswerable": 50, "removed": 40})
    dev += [r for _, r in dev_hp]

    sealed = take(
        ((None, k, r) for _, k, r in squad(rng, RAW / "squad_val.parquet")),
        {"answer": 60, "unanswerable": 50, "removed": 40},
    )
    sealed += [r for _, r in hotpot(rng, RAW / "hotpot_val.parquet", 100)]
    sealed += list(longmemeval(rng, RAW / "lme_oracle.json", 100))
    for q, lines, gold in FIXTURES:
        sealed.append(row(rng, "fixture", q, lines, gold))

    rng.shuffle(train)
    rng.shuffle(dev)
    manifest = {
        "seed": 17,
        "raw_sha256": HASHES,
        "files": {
            "train.jsonl": write("train.jsonl", train),
            "dev.jsonl": write("dev.jsonl", dev),
            "eval_sealed.jsonl": write("eval_sealed.jsonl", sealed),
        },
        "counts": {
            n: {
                "rows": len(rs),
                "empty_targets": sum(not r["target"] for r in rs),
                "by_source": {s: sum(r["source"] == s for r in rs) for s in sorted({r["source"] for r in rs})},
            }
            for n, rs in (("train", train), ("dev", dev), ("eval_sealed", sealed))
        },
        "splits": "SQuAD train articles split 90/10 into train/dev by title; SQuAD validation, "
        "HotpotQA validation, LongMemEval and fixtures are sealed evaluation only.",
        "licenses": {
            "squad2": "CC BY-SA 4.0, rajpurkar/squad_v2",
            "hotpotqa": "CC BY-SA 4.0, hotpotqa/hotpot_qa distractor",
            "longmemeval": "MIT, xiaowu0162/longmemeval-cleaned (oracle), evaluation only",
            "fixture": "Project-authored fictional notes, evaluation only",
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
