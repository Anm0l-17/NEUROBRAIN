"""Replay the fixed retrieval question set: recall@5 of search(), and v2 selector answers.

PYTHONPATH=src NEUROBRAIN_SELECTOR_MODEL=neurobrain-selector-v2 \
  .venv/bin/python reports/retrieval_v1/run.py [--no-selector] [--hybrid] > out.json
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.extract import answer, extract_notes

HERE = Path(__file__).parent


def build(store, pages):
    for page in pages:
        notes = [{"kind": "fact", "quote": n} for n in page["notes"]]
        ex = extract_notes(page["text"], page["source"], "page-api", lambda _: {"notes": notes})
        store.import_observation(page["text"], ex)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-selector", action="store_true")
    parser.add_argument("--hybrid", action="store_true", help="also report semantic.hybrid_search recall")
    args = parser.parse_args()
    fixture = json.loads((HERE / "fixture.json").read_text())
    encoder = None
    if args.hybrid:
        from neurobrain.semantic import hybrid_search, load_encoder

        encoder, error = load_encoder()
        if encoder is None:
            sys.exit(error)
    rows = []
    with tempfile.TemporaryDirectory() as d, MemoryStore(Path(d) / "m.sqlite3", Path(d)) as store:
        build(store, fixture["pages"])
        for item in fixture["questions"]:
            targets = set(item["targets"])
            top = [e["text"] for e in store.search(item["q"], limit=5)]
            row = {"set": item["set"], "q": item["q"], "top5": top,
                   "retrieved": bool(targets & set(top)) if targets else None}
            if encoder is not None:
                hybrid = [e["text"] for e in hybrid_search(store, item["q"], encoder)[0]]
                row["hybrid_retrieved"] = bool(targets & set(hybrid)) if targets else None
            if not args.no_selector:
                cited = [a["text"] for a in answer(store, item["q"])["answers"]]
                row["answer"] = cited
                row["correct"] = (bool(targets & set(cited)) if targets else not cited)
            rows.append(row)
    answerable = [r for r in rows if r["retrieved"] is not None]
    summary = {"selector": os.environ.get("NEUROBRAIN_SELECTOR_MODEL") or "qwen3.5:4b (default)",
               "recall@5": f"{sum(r['retrieved'] for r in answerable)}/{len(answerable)}"}
    if encoder is not None:
        summary["hybrid recall@5"] = f"{sum(r['hybrid_retrieved'] for r in answerable)}/{len(answerable)}"
    if not args.no_selector:
        summary["answered correctly"] = f"{sum(r['correct'] for r in answerable)}/{len(answerable)}"
        misses = [r for r in rows if r["retrieved"] is None]
        summary["near misses with no evidence"] = f"{sum(r['correct'] for r in misses)}/{len(misses)}"
    json.dump({"summary": summary, "rows": rows}, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
