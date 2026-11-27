"""Replay dev rows the adapter could not answer on Kaggle, through Ollama. Diagnostic only; not gated.

PYTHONPATH=src python3 reports/selector_v3/kaggle_failed_rows.py DEV_ADAPTER_JSON > kaggle_failed_rows.json

"app" is the app's exact request (extract.selection_payload, which constrains the reply to the shown IDs).
"unconstrained" is the same request without that JSON schema, which is closer to how Kaggle generated.
"""

import json
import sys
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from neurobrain.extract import selection_payload

ROOT = Path(__file__).resolve().parents[2]
rows = [json.loads(x) for x in (ROOT / "data/selector_v3/dev.jsonl").read_text().splitlines()]
kaggle = json.loads(Path(sys.argv[1]).read_text())["predictions"]
failed = [i for i, p in enumerate(kaggle) if p is None]
picked, seen = [], {}
for i in failed:  # up to two per source, in file order
    if seen.setdefault(rows[i]["source"], 0) < 2:
        picked.append(i)
        seen[rows[i]["source"]] += 1


def ask(payload):
    request = Request("http://127.0.0.1:11434/api/chat", json.dumps(payload).encode(),
                      {"Content-Type": "application/json"})
    with build_opener(ProxyHandler({})).open(request, timeout=120) as response:
        reply = json.load(response)
    return {"done_reason": reply.get("done_reason"), "content": reply["message"]["content"][:600]}


out = []
for i in picked:
    row = rows[i]
    payload = selection_payload(row["question"], row["evidence"], "neurobrain-selector-v3")
    app = ask(payload)
    del payload["format"]
    out.append(dict(index=i, source=row["source"], gold=row["target"], shown=len(row["evidence"]),
                    app=app, unconstrained=ask(payload)))
print(json.dumps(dict(failed_on_kaggle=len(failed), of=len(rows), replayed=out), indent=1))
