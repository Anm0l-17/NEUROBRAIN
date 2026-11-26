"""Build citation-selector v3 training, development and sealed evaluation rows.

Each row mirrors the app's real Ollama request (`extract.selection_payload`): a
question plus one to five evidence lines with 32-hex citation IDs, and the target
`{"citations": [...]}`, which is empty when no line answers the question.

Sources (downloaded by hand into .neurobrain/raw, hashes pinned below):
  SQuAD 2.0 (CC BY-SA 4.0), HotpotQA distractor (CC BY-SA 4.0): train + dev + eval
  LongMemEval oracle (MIT): train + dev + eval, split by question
  Our fictional demo fixtures: sealed evaluation only

v2 vs v1 (data/selector_v1, built at b5d9674): adapter v1 over-abstained because SQuAD train
rows were 52% empty and no conversation-style rows were trained on. v2 lowers SQuAD empties,
adds LongMemEval to train and dev, and draws a fresh sealed set with v1's quotas that shares
no question or evidence line with the retired v1 sealed set.

v3 vs v2 (data/selector_v2, built at 8496da4): adapter v2 cites the outdated line when a page also
records a change ("Dues are $5" over "dues went up to $8"), because v2 excluded knowledge-update rows.
v3 keeps v2's mix and adds update rows: the old and the new line are both in the evidence and the
gold is the line with the current value only (the app shows cited lines verbatim, so citing the old
one shows a wrong answer). Sources: project-written templates (train/dev use one set of attribute
families and names, the sealed update file a disjoint set) and LongMemEval knowledge-update
questions whose newer turn states the answer and whose older turn does not (the selector sees no
dates). Update rows are sealed in their own file, eval_update_sealed.jsonl, so eval_sealed.jsonl is
scored exactly as v2's was. The sealed sets share no question or evidence line with v1's or v2's.

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
OUT = ROOT / "data/selector_v3"
RETIRED = [ROOT / "data/selector_v1/eval_sealed.jsonl", ROOT / "data/selector_v2/eval_sealed.jsonl"]
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


def row(rng, source, question, lines, gold, keep=(), stale=()):
    """lines: 5 texts, closest distractors first; gold: indexes that answer.

    The app's search returns 1 to 5 lines, so keep every gold line (and every `keep`/`stale`
    line) plus the closest distractors up to a random count in that range, then shuffle and
    assign citations. stale: outdated lines an update row must show next to the current one.
    """
    assert len(lines) == 5 and len(set(lines)) == 5
    must = set(gold) | set(keep) | set(stale)
    n = rng.randint(max(1, len(must)), 5)
    extra = [i for i in range(5) if i not in must][: n - len(must)]
    return render(rng, source, question, lines, sorted(must) + extra, gold, stale)


def render(rng, source, question, lines, order, gold, stale=()):
    order = list(order)
    rng.shuffle(order)
    evidence = [{"citation": cite(rng), "text": lines[i]} for i in order]
    target = [e["citation"] for e, i in zip(evidence, order) if i in gold]
    user = json.dumps({"question": question, "evidence": evidence})
    out = {"source": source, "question": question, "evidence": evidence, "target": target}
    if stale:
        out["stale"] = [e["citation"] for e, i in zip(evidence, order) if i in stale]
    out["messages"] = [
        {"role": "system", "content": SELECT_SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": json.dumps({"citations": target})},
    ]
    return out


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
        variants = {v.lower() for v in answers["text"]}
        others = [s for s in closest(q, texts, 6, exclude=hit) if not any(v in s.lower() for v in variants)]
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
        others = [s for s in closest(q, pool, 8, exclude=gold) if ans.lower() not in s.lower()]
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


def longmemeval(rng, path):
    """Yield (kind, (question, lines, gold)) for every usable question; render with lme_row.

    kind: answer | abstain | removed. Returned unrendered so train can render a question
    several times (different evidence count, order and IDs).
    """
    data = json.load(open(path))
    rng.shuffle(data)
    for x in data:
        abstain = x["question_id"].endswith("_abs")
        # knowledge-update marks both old and new values as answers; assistant/preference
        # answers are not in user turns; temporal-reasoning answers need session dates.
        if x["question_type"] not in ("single-session-user", "multi-session"):
            continue
        turns = [t for s in x["haystack_sessions"] for t in s if t["role"] == "user"]
        gold = list(dict.fromkeys(t["content"].strip() for t in turns if t.get("has_answer")))
        if not 1 <= len(gold) <= 3 or any(len(g) > 600 for g in gold):
            continue
        pool = [t["content"].strip() for t in turns if len(t["content"]) <= 600]
        others = closest(x["question"], pool, 8, exclude=gold)
        ans = str(x["answer"]).lower()
        short = len(ans) <= 40  # short answers can be matched; long ones are explanations
        if short:
            others = [o for o in others if ans not in o.lower()]
        # Removed: drop the answering turns for a same-topic near miss (only when the answer
        # filter ran, so no distractor can still answer).
        if not abstain and short and rng.random() < 0.2 and len(others) >= 5:
            yield "removed", (x["question"], others[:5], set())
            continue
        if len(others) < 5 - len(gold):
            continue
        lines = gold + others[: 5 - len(gold)]
        # Abstention questions point at a related fact that does not answer them.
        gold_idx = set() if abstain else set(range(len(gold)))
        yield ("abstain" if abstain else "answer"), (x["question"], lines, gold_idx)


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


def answer_variants(answer):
    a = str(answer).strip().rstrip(".")
    parts = [a] + re.split(r"\s*\(or |\)|\s+or\s+", a)
    return sorted({p.strip().lower() for p in parts if len(p.strip()) >= 2})


def lme_updates(rng, path):
    """Yield (kind, (question, lines, gold, keep, stale)) for LongMemEval knowledge-update questions.

    The app shows no dates, so keep only questions whose newest answering turn states the answer
    and whose older answering turns do not; gold is that newest turn, the older turns are stale.
    """
    data = json.load(open(path))
    rng.shuffle(data)
    for x in data:
        if x["question_type"] != "knowledge-update":
            continue
        turns = [(d, t["content"].strip()) for s, d in zip(x["haystack_sessions"], x["haystack_dates"]) for t in s if t["role"] == "user"]
        pool = [c for _, c in turns if len(c) <= 600]
        if x["question_id"].endswith("_abs"):
            lines = closest(x["question"], pool, 5)
            if len(lines) == 5:
                yield "abstain", (x["question"], lines, set(), (), ())
            continue
        answering = [(d, c) for (d, c), t in zip(turns, (t for s in x["haystack_sessions"] for t in s if t["role"] == "user")) if t.get("has_answer")]
        if len(answering) < 2 or any(len(c) > 700 for _, c in answering):
            continue
        last = max(d for d, _ in answering)
        newer = list(dict.fromkeys(c for d, c in answering if d == last))
        older = list(dict.fromkeys(c for d, c in answering if d != last))
        vs = answer_variants(x["answer"])
        if len(newer) != 1 or not older or len(older) > 2:
            continue
        if not any(v in newer[0].lower() for v in vs) or any(v in o.lower() for v in vs for o in older):
            continue
        others = [o for o in closest(x["question"], pool, 8, exclude=newer + older) if not any(v in o.lower() for v in vs)]
        lines = newer + older + others[: 4 - len(older)]
        if len(lines) != 5:
            continue
        stale = set(range(1, 1 + len(older)))
        yield "update", (x["question"], lines, {0}, (), stale)


# Update templates, written for this project. {E}: entity as used in a sentence ("the Maple choir",
# "Ravi"); {N}: name without article; {o}/{n}: old and new value; {f}: fee noun; {up}/{grow}:
# direction words. Train and dev use TRAIN_FAMILIES; the sealed update file uses SEALED_FAMILIES,
# names and entity kinds that never appear in train. Book-club words (dues, Daniel, Aisha) never do.
TRAIN_FAMILIES = {
    "weekday": dict(
        type="group", values=["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"],
        old=["{E} meets on {o}.", "Meetings of {E} are held on {o}."],
        new=["{E} moved its meetings to {n}.", "{E} now meets on {n} instead of {o}.", "Meetings of {E} switched from {o} to {n}."],
        q=["What day does {E} meet?", "On which day are meetings of {E} held?"],
        orig="What day did {E} meet at first?",
    ),
    "venue": dict(
        type="group",
        values=["the town hall", "the community centre", "St. Mark's church hall", "the Greenway library", "the old fire station", "Hollis Park pavilion", "the Riverside school gym", "Bramble Cafe"],
        old=["{E} meets at {o}.", "{E} uses {o} for its meetings."],
        new=["{E} now meets at {n}.", "{E} left {o} and moved to {n}.", "The meeting place for {E} changed to {n}."],
        q=["Where does {E} meet?", "What is the meeting place for {E}?"],
        orig="Where did {E} meet originally?",
    ),
    "start": dict(
        type="group", values=["5:30 pm", "6:00 pm", "6:30 pm", "7:00 pm", "7:30 pm", "8:00 pm", "9:00 am", "10:00 am"],
        old=["Sessions of {E} start at {o}."],
        new=["Sessions of {E} now start at {n}.", "{E} moved its start time from {o} to {n}.", "From now on, sessions of {E} start at {n} instead of {o}."],
        q=["What time do sessions of {E} start?", "When do {N} sessions begin?"],
        orig="What time did sessions of {E} start originally?",
    ),
    "fee": dict(
        type="group", values=["$10", "$12", "$15", "$18", "$20", "$25", "$30", "$40"],
        old=["The {f} for {E} is {o}.", "{E} charges a {f} of {o}."],
        new=["The {f} for {E} {up} to {n}.", "{E} changed its {f} to {n}.", "The {f} for {E} is now {n}, no longer {o}."],
        q=["How much is the {f} for {E}?", "What does {E} charge as its {f}?"],
        orig="How much was the {f} for {E} at first?",
    ),
    "lead": dict(
        type="group", values="PEOPLE",
        old=["{o} runs {E}.", "{E} is organised by {o}."],
        new=["{o} handed {E} over to {n}.", "{n} took over running {E}.", "{E} is now organised by {n}."],
        q=["Who runs {E}?", "Who organises {E}?"],
        orig="Who ran {E} at the start?",
    ),
    "deadline": dict(
        type="group", values=["3 March", "14 March", "2 April", "20 April", "5 May", "18 May", "1 June", "12 June"],
        old=["The {N} newsletter is due on {o}."],
        new=["The {N} newsletter deadline was pushed to {n}.", "The {N} newsletter is now due on {n}.", "The {N} newsletter is due on {n}, not {o}."],
        q=["When is the {N} newsletter due?", "What is the deadline for the {N} newsletter?"],
        orig="When was the {N} newsletter first due?",
    ),
    "members": dict(
        type="group", values=["12", "15", "18", "20", "24", "30", "35", "40"],
        old=["{E} has {o} members."],
        new=["{E} {grow} to {n} members.", "{E} now has {n} members.", "Membership of {E} changed from {o} to {n}."],
        q=["How many members does {E} have?"],
        orig="How many members did {E} start with?",
    ),
    "chat": dict(
        type="group", values=["WhatsApp", "Slack", "Discord", "Signal", "Telegram", "email", "Microsoft Teams"],
        old=["{E} coordinates on {o}."],
        new=["{E} moved its chat from {o} to {n}.", "{E} now uses {n} instead of {o}.", "{E} switched to {n} for coordination."],
        q=["Which app does {E} use to coordinate?", "Where does {E} coordinate?"],
        orig="Which app did {E} use to coordinate before?",
    ),
    "city": dict(
        type="person", values=["Pune", "Leeds", "Lisbon", "Austin", "Nairobi", "Osaka", "Bristol", "Toronto", "Krakow", "Adelaide"],
        old=["{E} lives in {o}."],
        new=["{E} moved to {n}.", "{E} relocated from {o} to {n}.", "{E} now lives in {n}."],
        q=["Where does {E} live?", "Which city does {E} live in?"],
        orig="Where did {E} live before?",
    ),
    "job": dict(
        type="person", values=["a nurse", "a teacher", "a software engineer", "an accountant", "a chef", "an architect", "a pharmacist", "a graphic designer"],
        old=["{E} works as {o}."],
        new=["{E} changed careers and is now {n}.", "{E} started a new job as {n}.", "{E} no longer works as {o}; {E} is now {n}."],
        q=["What does {E} do for work?", "What is {E}'s job?"],
        orig="What was {E}'s job before?",
    ),
}
SEALED_FAMILIES = {
    "frequency": dict(
        type="group", values=["once a week", "twice a week", "every other week", "once a month", "twice a month", "three times a week"],
        old=["{E} gets together {o}."],
        new=["{E} now gets together {n}.", "{E} went from meeting {o} to meeting {n}.", "{E} decided to get together {n} instead of {o}."],
        q=["How often does {E} get together?"],
        orig="How often did {E} get together at first?",
    ),
    "extension": dict(
        type="group", values=["extension 112", "extension 205", "extension 318", "extension 427", "extension 530", "extension 641"],
        old=["Calls about {E} go to {o}."],
        new=["Calls about {E} now go to {n}.", "{E} changed its phone line from {o} to {n}."],
        q=["Which phone extension handles calls about {E}?", "What extension do I call about {E}?"],
        orig="Which extension did calls about {E} go to before?",
    ),
    "storage": dict(
        type="group", values=["locker 4", "the basement storeroom", "Room 12", "the blue shed", "the loft above the hall"],
        old=["{E} stores its equipment in {o}."],
        new=["{E} moved its equipment to {n}.", "The equipment for {E} is now kept in {n}."],
        q=["Where does {E} keep its equipment?"],
        orig="Where did {E} keep its equipment before?",
    ),
    "car": dict(
        type="person", values=["a red Corolla", "a grey Golf", "a white Civic", "a blue Model 3", "a green Fiesta", "a black Octavia"],
        old=["{E} drives {o}."],
        new=["{E} now drives {n}.", "{E} replaced {o} with {n}.", "{E} no longer drives {o}; {E} bought {n}."],
        q=["What car does {E} drive?"],
        orig="What car did {E} drive before?",
    ),
    "drink": dict(
        type="person", values=["black coffee", "green tea", "chai", "hot chocolate", "oat-milk lattes", "mint tea"],
        old=["{E} drinks {o} in the morning."],
        new=["{E} gave up {o} and switched to {n}.", "{E} drinks {n} in the morning now.", "These days {E} starts the morning with {n}."],
        q=["What does {E} drink in the morning?"],
        orig="What did {E} drink in the morning before?",
    ),
}
# One old line holding two attributes, like "Dues are $5 a month, collected by Daniel".
COMBOS = {
    ("weekday", "venue"): "{E} meets on {o1} at {o2}.",
    ("fee", "lead"): "{E} charges a {f} of {o1} and is organised by {o2}.",
    ("city", "job"): "{E} lives in {o1} and works as {o2}.",
    ("frequency", "storage"): "{E} gets together {o1} and keeps its equipment in {o2}.",
    ("car", "drink"): "{E} drives {o1} and drinks {o2} in the morning.",
}
FILLERS = {
    "group": ["{E} was founded in 2019.", "{E} keeps a shared photo album.", "{E} has a written code of conduct.", "{E} raised money for the food bank last year."],
    "person": ["{E} has two cats.", "{E} is allergic to peanuts.", "{E} plays the cello.", "{E} grew up near the coast.", "{E} is learning Spanish.", "{E} supports the local football team."],
}
NAMES = {  # split -> (group words, group kinds, people)
    "train": (
        ["Maple", "Cedar", "Northside", "Riverbend", "Elm Street", "Hillcrest", "Oakwood", "Bayview", "Lakeside", "Pinecrest"],
        ["chess club", "choir", "running group", "study group", "garden committee", "robotics team"],
        ["Ravi", "Meera", "Tomas", "Grace", "Kenji", "Lucia", "Omar", "Hannah", "Arjun", "Sofia", "Felix", "Nadia"],
    ),
    "dev": (["Foxglove", "Brookfield", "Ashford"], ["quiz team", "hiking club"], ["Ivan", "Leila", "Bruno", "Mei"]),
    "sealed": (
        ["Juniper", "Copperfield", "Westgate", "Stonebridge", "Larkspur", "Thornbury"],
        ["film society", "pottery circle", "climbing crew", "debate team"],
        ["Yusuf", "Elena", "Marcus", "Anika", "Pablo", "Ingrid", "Kofi", "Selin"],
    ),
}
FEE_NOUNS = ["membership fee", "monthly subscription", "entry fee"]
KINDS = {"current": 35, "sibling": 15, "original": 8, "lone_old": 10, "lone_update": 10, "absent": 22}


def cap(text):
    return text[0].upper() + text[1:]


def number(value):
    return float(re.search(r"\d+", value).group())


def synthetic(rng, split, count):
    """Yield update rows from templates: (kind, (question, lines, gold, keep, stale))."""
    fams = SEALED_FAMILIES if split == "sealed" else TRAIN_FAMILIES
    words_, kinds_, people = NAMES[split]
    made = 0
    while made < count:
        kind = rng.choices(list(KINDS), weights=list(KINDS.values()))[0]
        F = rng.choice(sorted(fams))
        typ = fams[F]["type"]
        if typ == "group":
            name, other_name = rng.sample([f"{w} {k}" for w in words_ for k in kinds_], 2)
            ent, other = (f"the {name}", name), (f"the {other_name}", other_name)
        else:
            a, b = rng.sample(people, 2)
            ent, other = (a, a), (b, b)
        f = rng.choice(FEE_NOUNS)
        vals = {}
        for fam in fams:
            pool = people if fams[fam]["values"] == "PEOPLE" else fams[fam]["values"]
            vals[fam] = rng.sample([v for v in pool if v not in (ent[0], other[0])], 2)

        def fill(template, e=ent, fam=None, **kw):
            o, n = vals[fam] if fam else ("", "")
            up = grow = ""
            if fam in ("fee", "members"):
                up = "went up" if number(n) > number(o) else "dropped"
                grow = "has grown" if number(n) > number(o) else "has shrunk"
            return cap(template.format(E=e[0], N=e[1], o=o, n=n, f=f, up=up, grow=grow, **kw))

        def old(fam, e=ent):
            return fill(rng.choice(fams[fam]["old"]), e, fam)

        def new(fam, mention_old=True):
            # An "original" question needs an update line that does not also state the old value.
            return fill(rng.choice([t for t in fams[fam]["new"] if mention_old or "{o}" not in t]), ent, fam)

        same = [g for g in sorted(fams) if fams[g]["type"] == typ and g != F]
        G = rng.choice(same)
        combo = next((c for c in COMBOS if set(c) == {F, G}), None)
        combo_line = None
        if combo:
            combo_line = fill(COMBOS[combo], o1=vals[combo[0]][0], o2=vals[combo[1]][0])
        use_combo = combo_line is not None and rng.random() < 0.5
        asked = F
        if kind == "current":  # gold: the update; stale: the old line
            core = [new(F), combo_line if use_combo else old(F)]
            gold, keep, stale = {0}, set(), {1}
        elif kind == "original":
            core = [combo_line if use_combo else old(F), new(F, mention_old=False)]
            gold, keep, stale = {0}, {1}, set()
        elif kind == "sibling":  # only another attribute changed; F's old line still answers
            core = [combo_line, new(G)] if use_combo else [old(F), old(G), new(G)]
            gold, keep, stale = {0}, set(range(1, len(core))), set()
        elif kind == "lone_old":
            core, gold, keep, stale = [old(F)], {0}, set(), set()
        elif kind == "lone_update":
            core, gold, keep, stale = [new(F)], {0}, set(), set()
        else:  # absent: the asked attribute is not in the evidence at all
            asked = G
            core = [old(F), new(F)]
            gold, keep, stale = set(), {0, 1}, set()
        used = {F, G} if kind in ("sibling", "absent") or use_combo else {F}
        near = [old(asked, other)]  # same attribute, different entity: never answers
        rest = [old(g) for g in same if g not in used] + [fill(t) for t in FILLERS[typ]]
        rng.shuffle(rest)
        cand = (near + rest) if rng.random() < 0.5 else (rest[:1] + near + rest[1:])
        lines = core + [c for c in cand if c not in core][: 5 - len(core)]
        if len(lines) != 5 or len(set(lines)) != 5:
            continue
        question = fill(rng.choice(fams[asked]["q"] if kind != "original" else [fams[F]["orig"]]))
        made += 1
        yield kind, (question, lines, gold, keep, stale)


BOOK = [  # notes stored from the user's book-club page (reports/selector_v2/README.md, live check)
    "The Harbor Lights book club meets on the first Thursday of every month at Corner Grind Café on Wharf Road, starting at 7:00 pm.",
    "members are asked to finish it by chapter 18",
    "Dues are $5 a month, collected by Daniel, who keeps a spreadsheet of who has paid.",
    "Parking is free on the street after 6 pm.",
    "meetings would move to the second Thursday",
    "too many members had a clash with a school event",
    "Corner Grind closed for renovation",
    "club now meets at the Wharf Road public library in Meeting Room B, at 6:30 pm instead of 7:00",
    "Priya stepped back as organizer in March and handed book selection to Daniel",
    "Collecting dues then passed to a new member, Aisha",
    "dues went up to $8 a month to cover the library room fee",
    "The current book is no longer The Glass Orchard",
    "The group dropped it halfway through and switched to Salt and Signal",
]
BOOK_FIXTURES = [  # (question, evidence indexes into BOOK, gold, stale); every line is shown
    ("How much are the dues?", [2, 9, 10, 3, 0], {10}, {2}),
    ("Who collects the dues?", [2, 9, 10, 8, 3], {9}, {2}),
    ("Where does the book club meet?", [0, 6, 7, 3, 4], {7}, {0}),
    ("What time does the book club start?", [0, 7, 4, 3, 6], {7}, {0}),
    ("Which Thursday does the book club meet?", [0, 4, 5, 7, 3], {4}, {0}),
    ("Who picks the books?", [8, 1, 11, 12, 3], {8}, set()),
    ("What is the current book?", [11, 12, 1, 8, 3], {12}, {1}),
    ("How much is the library room fee?", [10, 7, 9, 2, 3], set(), set()),
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
    upd_rng = random.Random(23)  # update rows draw from their own stream
    retired = [json.loads(line) for path in RETIRED for line in open(path)]
    old_questions = {r["question"] for r in retired if r["source"] != "fixture"}
    old_lines = {e["text"] for r in retired if r["source"] != "fixture" for e in r["evidence"]}

    titles = sorted({r["title"] for r in pq.read_table(RAW / "squad_train.parquet", columns=["title"]).to_pylist()})
    rng.shuffle(titles)
    dev_titles = set(titles[: len(titles) // 10])  # grouped by article: no shared paragraphs
    train_titles = set(titles) - dev_titles

    def take(stream, quota):
        got = {k: [] for k in quota}
        for _, kind, r in stream:
            if kind in quota and len(got[kind]) < quota[kind]:
                got[kind].append(r)
            if all(len(got[k]) >= quota[k] for k in quota):
                break
        return [r for k in quota for r in got[k]]

    def fresh(stream):
        """Sealed v3 candidates: nothing the v1 or v2 sealed sets (each used for a decision) showed."""
        for item in stream:
            r = item[-1]
            if r["question"] not in old_questions and not any(e["text"] in old_lines for e in r["evidence"]):
                yield item

    # Same SQuAD and HotpotQA mix as v2 (SQuAD train 22% empty).
    train = take(squad(rng, RAW / "squad_train.parquet", train_titles), {"answer": 900, "unanswerable": 150, "removed": 100})
    hp = list(hotpot(rng, RAW / "hotpot_train0.parquet", 1550))
    train += [r for _, r in hp[:1400]]
    dev = take(squad(rng, RAW / "squad_train.parquet", dev_titles), {"answer": 60, "unanswerable": 50, "removed": 40})
    dev += [r for _, r in hp[1400:]]

    # LongMemEval single-session-user/multi-session: every question was shown by the v1 or v2
    # sealed set or trained on by v2, so none is fresh; all go to dev (30) and train (x3 renders).
    lme = [args for _, args in longmemeval(rng, RAW / "lme_oracle.json")]
    dev += [row(rng, "longmemeval", *a) for a in lme[:30]]
    train += [row(rng, "longmemeval", *a) for a in lme[30:] for _ in range(3)]

    # Update rows. LongMemEval knowledge-update, split by question: 40% sealed, 10% dev, rest train.
    ku = list(lme_updates(upd_rng, RAW / "lme_oracle.json"))
    n_sealed, n_dev = len(ku) * 2 // 5, len(ku) // 10

    def ku_row(args):
        return row(upd_rng, "longmemeval_update", *args)

    sealed_upd = [ku_row(a) for _, a in ku[:n_sealed]]
    dev += [ku_row(a) for _, a in ku[n_sealed : n_sealed + n_dev]]
    train += [ku_row(a) for _, a in ku[n_sealed + n_dev :] for _ in range(3)]
    # Templates: train/dev share attribute families (different names); sealed has its own.
    train += [row(upd_rng, f"update_{k}", *a) for k, a in synthetic(upd_rng, "train", 700)]
    dev += [row(upd_rng, f"update_{k}", *a) for k, a in synthetic(upd_rng, "dev", 60)]
    sealed_upd += [row(upd_rng, f"update_{k}", *a) for k, a in synthetic(upd_rng, "sealed", 240)]
    sealed_upd += [
        render(upd_rng, "fixture_update", q, [BOOK[i] for i in idx], range(5), gold={idx.index(g) for g in gold}, stale={idx.index(s) for s in stale})
        for q, idx, gold, stale in BOOK_FIXTURES
    ]

    sealed = take(
        fresh((None, k, r) for _, k, r in squad(rng, RAW / "squad_val.parquet")),
        {"answer": 60, "unanswerable": 50, "removed": 40},
    )
    sealed += [r for _, r in fresh(hotpot(rng, RAW / "hotpot_val.parquet", 300))][:100]
    # The same 15 fixture rows as v1 and v2 (same evidence and IDs), so fixture results compare.
    fixtures = [r for r in retired if r["source"] == "fixture"][-len(FIXTURES):]
    assert [r["question"] for r in fixtures] == [q for q, _, _ in FIXTURES]
    sealed += fixtures

    # Drop dev and sealed rows that reuse any evidence line seen in an earlier split.
    seen = {e["text"] for r in train for e in r["evidence"]}
    dev = [r for r in dev if not any(e["text"] in seen for e in r["evidence"])]
    seen |= {e["text"] for r in dev for e in r["evidence"]}
    sealed = [r for r in sealed if r["source"] == "fixture" or not any(e["text"] in seen for e in r["evidence"])]
    sealed_upd = [r for r in sealed_upd if not any(e["text"] in seen for e in r["evidence"])]
    for r in sealed + sealed_upd:  # the retired v1 and v2 sealed sets must not leak into v3's
        if r["source"] != "fixture":
            assert r["question"] not in old_questions and not any(e["text"] in old_lines for e in r["evidence"])
    assert sum(r["source"] == "fixture_update" for r in sealed_upd) == len(BOOK_FIXTURES)
    banned = re.compile(r"\b(dues|Daniel|Aisha|Harbor Lights)\b")  # book-club words stay out of training
    assert not any(banned.search(r["messages"][1]["content"]) for r in train + dev if r["source"].startswith("update_"))
    rng.shuffle(train)
    rng.shuffle(dev)
    splits = (("train", train), ("dev", dev), ("eval_sealed", sealed), ("eval_update_sealed", sealed_upd))
    manifest = {
        "seed": 17,
        "update_seed": 23,
        "raw_sha256": HASHES,
        "files": {f"{n}.jsonl": write(f"{n}.jsonl", rs) for n, rs in splits},
        "counts": {
            n: {
                "rows": len(rs),
                "empty_targets": sum(not r["target"] for r in rs),
                "by_source": {
                    s: {"rows": sum(r["source"] == s for r in rs), "empty": sum(r["source"] == s and not r["target"] for r in rs)}
                    for s in sorted({r["source"] for r in rs})
                },
            }
            for n, rs in splits
        },
        "splits": "SQuAD train articles split 90/10 into train/dev by title; SQuAD validation and HotpotQA "
        "validation are sealed only; LongMemEval single-session/multi-session questions go to dev and train "
        "(none is unseen); LongMemEval knowledge-update split by question 40/10/50 into sealed-update/dev/train; "
        "update templates use disjoint attribute families, names and entity kinds for the sealed update file; "
        "fixtures sealed only. No sealed row shares a question or evidence line with the v1 or v2 sealed sets.",
        "update_policy": "Gold is the line holding the current value only; outdated lines are listed in 'stale'.",
        "licenses": {
            "squad2": "CC BY-SA 4.0, rajpurkar/squad_v2",
            "hotpotqa": "CC BY-SA 4.0, hotpotqa/hotpot_qa distractor",
            "longmemeval": "MIT, xiaowu0162/longmemeval-cleaned (oracle)",
            "update templates": "Project-authored fictional text",
            "fixture": "Project-authored fictional notes, evaluation only",
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
