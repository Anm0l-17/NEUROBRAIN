"""Fact recall of the real extraction model (Ollama qwen3.5:4b) on fixed fictional pages.

PYTHONPATH=src python reports/extraction_recall_v1/run.py [--set test] > out.json

A fact counts as kept when one stored note contains its key substring.

--set dev (default): the book club and Saffron Bridge pages from
reports/retrieval_v1/fixture.json plus dev_pages.json. All seven shaped the prompt or the
second pass, so they are development pages, not held-out evidence.
--set test: testset.json, written and locked before any variant ran on it; one run per
variant, nothing tuned afterwards.
"""

import json
import sys
import time
from pathlib import Path

from neurobrain.extract import extract_notes, generate

HERE = Path(__file__).parent
BOOK = ["first Thursday of every month", "founded it in 2023", "picks the books", "The Glass Orchard",
        "chapter 18", "$5 a month", "reserves the back table", "10% off drinks", "Parking is free",
        "second Thursday", "school event", "closed for renovation", "Meeting Room B", "6:30 pm",
        "book selection to Daniel", "new member, Aisha", "$8 a month", "no longer The Glass Orchard",
        "Salt and Signal", "chapter 10"]
SAFFRON = ["3 December 2026", "PostgreSQL", "request ID", "bullet-point", "vendor quote",
           "15 January 2027", "testing plan"]


def pages(which):
    if which == "test":
        yield from json.loads((HERE / "testset.json").read_text())
        return
    fixture = json.loads((HERE.parent / "retrieval_v1/fixture.json").read_text())["pages"]
    text = {p["source"]: p["text"] for p in fixture}
    yield dict(source="book-club", text=text["book-club"], facts=BOOK, chatter=[])
    yield dict(source="saffron-bridge", text=text["saffron-bridge"], facts=SAFFRON, chatter=[])
    yield from json.loads((HERE / "dev_pages.json").read_text())


def main():
    which = "test" if sys.argv[1:] == ["--set", "test"] else "dev"
    rows = []
    for page in pages(which):
        started = time.monotonic()
        raw = generate(page["text"])["notes"]
        kept = [n["text"] for n in extract_notes(page["text"], page["source"], "page-api",
                                                  lambda _, raw=raw: {"notes": raw})["notes"]]
        missed = [f for f in page["facts"] if not any(f in k for k in kept)]
        rows.append(dict(
            source=page["source"], facts=len(page["facts"]), found=len(page["facts"]) - len(missed),
            missed=missed, chatter_kept=[c for c in page["chatter"] if any(c in k for k in kept)],
            unmatched=[n["quote"] for n in raw if n["quote"].lower() not in page["text"].lower()],
            seconds=round(time.monotonic() - started, 1), notes=kept))
        print(f"{page['source']}: {rows[-1]['found']}/{rows[-1]['facts']} missed={missed}", file=sys.stderr)
    total = dict(found=sum(r["found"] for r in rows), facts=sum(r["facts"] for r in rows),
                 seconds=round(sum(r["seconds"] for r in rows), 1))
    print(json.dumps(dict(set=which, total=total, pages=rows), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
