"""Ask the app's answer() the same 20 book-club/demo questions on a COPY of the live DB, per selector model.

Copy first (never point this at the live file):
  sqlite3 -readonly "file:$ROOT/.neurobrain/observations.sqlite3?mode=ro" ".backup /tmp/live.sqlite3"
  PYTHONPATH=src python reports/live_check/score.py /tmp/live.sqlite3 $ROOT/examples/notes \
      qwen3.5:4b neurobrain-selector-v2 > out.json

Expects the book club Notion page saved (25-26 Nov 2026). Questions were written after seeing the stored notes:
a spot check, not a sealed score. "ok" on an update question needs the current line and no outdated line."""
import json, os, sys
from pathlib import Path
from neurobrain.core import MemoryStore
from neurobrain.extract import answer

STALE_TIME = ["first Thursday of every month at Corner Grind"]
# (question, gold substrings (any one cited = found), stale substrings (any cited = wrong))
QS = [
    ("Who picks the books?", ["book selection to Daniel"], []),
    ("What is the current book?", ["Salt and Signal", "no longer The Glass Orchard"], ["chapter 18"]),
    ("Where does the book club meet?", ["public library"], STALE_TIME),
    ("What time does the book club start?", ["6:30 pm"], STALE_TIME),
    ("Which Thursday does the book club meet on?", ["second Thursday"], STALE_TIME),
    ("Is parking free?", ["Parking is free"], []),
    ("Which chapter should we read up to?", ["chapter 10"], ["chapter 18"]),
    ("How much are the dues?", ["$8 a month"], ["$5 a month"]),
    ("Who collects the dues?", ["Aisha"], ["$5 a month"]),
    ("Why did the meetings move to the second Thursday?", ["school event"], []),
    ("Why did the book club venue change?", ["closed for renovation"], []),
    ("Why did the dues go up?", ["library room fee"], []),
    ("When is the amber lighthouse audit?", ["amber lighthouse audit"], []),
    ("When is the book club holiday party?", None, []),
    ("How much is the library room fee?", None, []),
    ("When is the Saffron Bridge kickoff?", None, []),
    ("When is the violet demonstration?", None, []),
    ("When is the amber lighthouse party?", None, []),
    ("What discount do members get at the library?", None, []),
    ("When is the pink submarine launch?", None, []),
]

db, root, models = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
out = {}
with MemoryStore(db, root) as store:
    for m in models:
        os.environ["NEUROBRAIN_SELECTOR_MODEL"] = m
        rows = []
        for q, gold, stale in QS:
            cited = [a["text"] for a in answer(store, q)["answers"]]
            if gold is None:
                ok, partial = not cited, False
            else:
                hit = any(g in c for g in gold for c in cited)
                bad = any(s in c for s in stale for c in cited)
                ok, partial = hit and not bad, hit and bad
            rows.append(dict(q=q, ok=ok, partial=partial, cited=cited))
        ans = [r for r, (_, g, _) in zip(rows, QS) if g is not None]
        nm = [r for r, (_, g, _) in zip(rows, QS) if g is None]
        out[m] = dict(answerable=f"{sum(r['ok'] for r in ans)}/{len(ans)}",
                      partial=sum(r['partial'] for r in ans),
                      refused_correctly=f"{sum(r['ok'] for r in nm)}/{len(nm)}",
                      total=f"{sum(r['ok'] for r in rows)}/{len(rows)}", rows=rows)
json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
