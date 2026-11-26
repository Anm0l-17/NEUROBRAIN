"""Questions beside reports/live_check/score.py, through the same answer(), on a scratch copy.
Set NEUROBRAIN_HYBRID=1 to measure the hybrid. Prints the top five and what the selector cited.

PYTHONPATH=src NEUROBRAIN_SELECTOR_MODEL=neurobrain-selector-v2 \
  python reports/hybrid_v1/extra_questions.py COPY.sqlite3 NOTES_ROOT
"""

import json
import sys
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.extract import answer, search_evidence

QS = ["Why did the venue change?", "Why did the book club venue change?",
      "Who founded the club?", "What discount do members get at the café?"]

with MemoryStore(Path(sys.argv[1]), Path(sys.argv[2])) as store:
    rows = [dict(q=q, top5=[e["text"] for e in search_evidence(store, q)],
                 cited=[a["text"] for a in answer(store, q)["answers"]]) for q in QS]
print(json.dumps(rows, indent=1, ensure_ascii=False))
