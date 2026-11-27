"""Build data/selector_v4: v3 train/dev plus teacher rows written and labelled by Sonnet (distillation).

Input: data/selector_v4/teacher_rows.jsonl, scenarios a Sonnet teacher wrote and a second, blind Sonnet
pass labelled the same way (rows where the two disagreed were dropped before this file was written).
v3's train.jsonl and dev.jsonl are read as they are; no sealed file is read except to check for overlap.

Run: uv run --no-project --with pyarrow python scripts/build_selector_v4.py
"""

import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_selector_data import MAX_LINE, row  # noqa: E402  (same row format and citation IDs as v3)

V3 = ROOT / "data/selector_v3"
OUT = ROOT / "data/selector_v4"
SEALED = [ROOT / "data/selector_v1/eval_sealed.jsonl", ROOT / "data/selector_v2/eval_sealed.jsonl",
          V3 / "eval_sealed.jsonl", V3 / "eval_update_sealed.jsonl"]
# Fixture facts, and the sealed update file's held-out names and attribute families.
BANNED = re.compile(
    r"\b(books?|book club|dues|daniel|aisha|priya|mira|rohan|harbor lights|saffron bridge|amber lighthouse|"
    r"violet demonstration|pink submarine|teal harbour|kestrel|wren|glass orchard|salt and signal|corner grind|"
    r"wharf road|meeting room b|library room fee|postgresql|juniper|copperfield|westgate|stonebridge|larkspur|"
    r"thornbury|film society|pottery circle|climbing crew|debate team|yusuf|elena|marcus|anika|pablo|ingrid|"
    r"kofi|selin|extension \d+|parking is free)\b", re.I)
NAMED = re.compile(r"book club|saffron bridge|amber lighthouse|violet demonstration|pink submarine", re.I)
KINDS = {"current", "two_attr", "split", "change", "sibling", "original", "lone", "near_miss"}
SEED, DEV_SHARE = 41, 0.1


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return [json.loads(line) for line in path.read_bytes().decode().splitlines()]


def text_of(r):
    return " ".join([r["question"]] + [e["text"] for e in r["evidence"]])


def main():
    sealed = [r for p in SEALED for r in load(p)]
    sealed_q = {r["question"].lower() for r in sealed}
    sealed_lines = {e["text"].lower() for r in sealed for e in r["evidence"]}

    scen = load(OUT / "teacher_rows.jsonl")
    kept, dropped = [], Counter()
    for s in scen:
        assert s["kind"] in KINDS and len(s["lines"]) == 5 and len(set(s["lines"])) == 5, s["id"]
        g, k, st = set(s["gold"]), set(s["keep"]), set(s["stale"])
        assert g | k | st <= set(range(5)) and not (g & k or g & st or k & st), s["id"]
        assert s["verifier_gold"] == sorted(g), s["id"]  # second pass agreed
        if BANNED.search(" ".join([s["question"]] + s["lines"])):
            dropped["banned"] += 1
        elif s["question"].lower() in sealed_q or any(t.lower() in sealed_lines for t in s["lines"]):
            dropped["sealed_overlap"] += 1
        elif any(len(t) > MAX_LINE for t in s["lines"]):
            dropped["too_long"] += 1
        else:
            kept.append(s)

    rng = random.Random(SEED)
    new = {"train": [], "dev": []}
    for s in kept:
        split = "dev" if rng.random() < DEV_SHARE else "train"
        new[split].append(row(rng, f"teacher_{s['kind']}", s["question"], s["lines"], set(s["gold"]),
                              keep=s["keep"], stale=s["stale"]))
    for r in new["train"] + new["dev"]:
        assert not BANNED.search(text_of(r))

    raw = {name: (V3 / name).read_bytes() for name in ("train.jsonl", "dev.jsonl")}
    files, counts = {}, {}
    for split in ("train", "dev"):
        # v3 lines are kept byte for byte; one epoch, so shuffle: teacher rows must not all come last
        lines = raw[f"{split}.jsonl"].decode().splitlines() + [json.dumps(r) for r in new[split]]
        rng.shuffle(lines)
        rows = [json.loads(line) for line in lines]
        data = "".join(line + "\n" for line in lines).encode()
        (OUT / f"{split}.jsonl").write_bytes(data)
        files[f"{split}.jsonl"] = sha(data)
        by = Counter(r["source"] for r in rows)
        counts[split] = {"rows": len(rows), "empty_targets": sum(not r["target"] for r in rows),
                         "teacher_rows": len(new[split]), "by_source": dict(sorted(by.items())),
                         "named_fixture_phrase_hits": sum(bool(NAMED.search(text_of(r))) for r in rows)}

    manifest = {
        "seed": SEED, "dev_share": DEV_SHARE,
        "inputs_sha256": {"selector_v3/" + n: sha(b) for n, b in raw.items()}
        | {"selector_v4/teacher_rows.jsonl": sha((OUT / "teacher_rows.jsonl").read_bytes())},
        "sealed_sha256_unchanged": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in SEALED},
        "teacher": {"scenarios": len(scen), "kept": len(kept), "dropped": dict(dropped),
                    "kept_by_kind": dict(sorted(Counter(s["kind"] for s in kept).items()))},
        "files": files, "counts": counts,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["teacher"], indent=2), json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
