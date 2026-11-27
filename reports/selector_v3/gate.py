"""The nine items of the v3 promotion gate (README.md), from two scripts/eval_selector.py outputs.

python3 reports/selector_v3/gate.py adapter_eval.json adapter_update_eval.json

An error (prediction null) never counts as a pass; for item 7 it counts as citing a stale line.
"""

import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data/selector_v3"


def load(name, out):
    rows = [json.loads(line) for line in (DATA / name).read_text().splitlines()]
    result = json.loads(Path(out).read_text())
    preds = [None if p is None else set(p) for p in result["predictions"]]
    assert len(preds) == len(rows), f"{out} does not cover {name}"
    return list(zip(rows, preds)), result["metrics"]["all"]


def exact(pairs):
    return sum(p is not None and p == set(r["target"]) for r, p in pairs)


def gate(sealed_out, update_out):
    sealed, m = load("eval_sealed.jsonl", sealed_out)
    update, um = load("eval_update_sealed.jsonl", update_out)

    def source(*names):
        return [(r, p) for r, p in update if r["source"] in names]

    answerable = [(r, p) for r, p in sealed if r["target"]]
    fixtures = [(r, p) for r, p in sealed if r["source"] == "fixture"]
    answered = [(r, p) for r, p in fixtures if r["target"]]
    near = [(r, p) for r, p in fixtures if not r["target"]]
    errors = sum(p is None for _, p in sealed + update)
    current = source("update_current")
    stale = [(r, p) for r, p in update if r.get("stale")]
    cited_stale = sum(p is None or bool(p & set(r["stale"])) for r, p in stale)
    club = source("fixture_update")
    dues = [(r, p) for r, p in club if "dues" in r["question"]]
    shortcut = source("update_sibling", "update_lone_old", "update_lone_update")
    recall, precision = m["abstain_recall"] or 0, m["abstain_precision"] or 0
    rows = [
        (1, f"abstain recall {recall:.3f} (min 0.50)", recall >= 0.50),
        (2, f"abstain precision {precision:.3f} (min 0.85)", precision >= 0.85),
        (3, f"answerable exact {exact(answerable)}/{len(answerable)} (min 83 and 107)",
         exact(answerable) >= max(83, 107)),
        (4, f"fixtures {exact(answered)}/{len(answered)}, near misses empty {exact(near)}/{len(near)} (9, min 5)",
         exact(answered) == len(answered) == 9 and exact(near) >= 5),
        (5, f"errors on both files {errors} (max 0)", errors == 0),
        (6, f"current value exact {exact(current)}/{len(current)} (min 69)", exact(current) >= 69),
        (7, f"stale line cited {cited_stale}/{len(stale)} (max 28)", cited_stale <= 28),
        (8, f"book club {exact(club)}/{len(club)}, dues {exact(dues)}/{len(dues)} (min 6, both dues)",
         exact(club) >= 6 and exact(dues) == len(dues) == 2),
        (9, f"sibling + lone {exact(shortcut)}/{len(shortcut)} (min 79), update-file abstain precision "
            f"{um['abstain_precision'] or 0:.3f} (min 0.85)",
         exact(shortcut) >= 79 and (um["abstain_precision"] or 0) >= 0.85),
    ]
    reported = {s: f"{exact(source(s))}/{len(source(s))}"
                for s in ("update_original", "update_absent", "longmemeval_update")}
    return rows, reported


if __name__ == "__main__":
    rows, reported = gate(*sys.argv[1:3])
    for number, text, ok in rows:
        print(number, "PASS" if ok else "FAIL", text)
    print("reported, not gated:", reported)
    print("GATE:", "PASS" if all(ok for *_, ok in rows) else "FAIL")
