"""The two questions about facts the old extraction dropped; reports/live_check/score.py stays unchanged.

PYTHONPATH=src python reports/extraction_recall_v1/extra_questions.py COPY.sqlite3 NOTES_ROOT MODEL...
"""

import json
import os
import sys
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.extract import answer

QS = [("Who founded the club?", "founded it in 2023"),
      ("What discount do members get at the café?", "10% off drinks")]

out = {}
with MemoryStore(Path(sys.argv[1]), Path(sys.argv[2])) as store:
    for model in sys.argv[3:]:
        os.environ["NEUROBRAIN_SELECTOR_MODEL"] = model
        rows = []
        for q, gold in QS:
            cited = [a["text"] for a in answer(store, q)["answers"]]
            rows.append(dict(q=q, ok=any(gold in c for c in cited), cited=cited,
                             top5=[e["text"] for e in store.search(q, limit=5)]))
        out[model] = rows
print(json.dumps(out, indent=1, ensure_ascii=False))
