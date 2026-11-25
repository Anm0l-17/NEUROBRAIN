"""Score an Ollama model on citation selection with the app's exact request.

Usage: PYTHONPATH=src python scripts/eval_selector.py data/selector_v1/eval_sealed.jsonl \
           --model qwen3.5:4b --out reports/selector_v1/base_eval.json
"""

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

from neurobrain.core import MemoryError
from neurobrain.extract import selection_payload, structured_request


def valid_citations(result, evidence):
    """The app's acceptance rule (extract.answer): a list of at most 5 known IDs, else None."""
    allowed = {e["citation"] for e in evidence}
    got = result.get("citations") if isinstance(result, dict) else None
    if not isinstance(got, list) or len(got) > 5 or any(not isinstance(c, str) or c not in allowed for c in got):
        return None
    return set(got)


def score(rows, preds):
    """Exact set match; abstention precision/recall; over- and under-selection.

    A None prediction is an error the app would raise on; it counts as a miss everywhere.
    """
    m = defaultdict(lambda: defaultdict(int))
    for r, p in zip(rows, preds):
        gold, pred = set(r["target"]), p
        for key in ("all", r["source"]):
            s = m[key]
            s["n"] += 1
            s["gold_empty"] += not gold
            s["answerable"] += bool(gold)
            if pred is None:
                s["errors"] += 1
                continue
            s["exact"] += pred == gold
            s["pred_empty"] += not pred
            s["abstain_tp"] += not gold and not pred
            if gold:
                s["over"] += bool(pred - gold)
                s["under"] += bool(gold - pred)
    out = {}
    for key, s in m.items():
        out[key] = {
            "n": s["n"],
            "exact_match": round(s["exact"] / s["n"], 3),
            "abstain_recall": round(s["abstain_tp"] / s["gold_empty"], 3) if s["gold_empty"] else None,
            "abstain_precision": round(s["abstain_tp"] / s["pred_empty"], 3) if s["pred_empty"] else None,
            "over_select_rate": round(s["over"] / s["answerable"], 3) if s["answerable"] else None,
            "under_select_rate": round(s["under"] / s["answerable"], 3) if s["answerable"] else None,
            "errors": s["errors"],
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows", type=Path)
    ap.add_argument("--model", default="qwen3.5:4b")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    rows = [json.loads(line) for line in args.rows.open()][: args.limit]
    preds, started = [], time.monotonic()
    for r in rows:
        try:
            got = structured_request(selection_payload(r["question"], r["evidence"], args.model))
            preds.append(valid_citations(got, r["evidence"]))
        except MemoryError:
            preds.append(None)
    metrics = score(rows, preds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "model": args.model,
                "rows": str(args.rows),
                "seconds": round(time.monotonic() - started, 1),
                "metrics": metrics,
                "predictions": [sorted(p) if p is not None else None for p in preds],
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
