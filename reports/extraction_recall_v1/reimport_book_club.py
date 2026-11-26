"""On a scratch COPY of the live DB, replace the book club page with a fresh extraction of the
retyped text (reports/retrieval_v1/fixture.json), under the live page's own key.

PYTHONPATH=src python reports/extraction_recall_v1/reimport_book_club.py COPY.sqlite3 NOTES_ROOT
"""

import json
import sys
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.extract import extract_notes

db, root = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
if db.name == "observations.sqlite3":
    sys.exit("Use a scratch copy, never the live database.")
fixture = json.loads((Path(__file__).parent.parent / "retrieval_v1/fixture.json").read_text())
text = fixture["pages"][0]["text"]
with MemoryStore(db, root) as store:
    page = next(
        s["observation"] for s in store.sources()
        if s["active"] and s.get("observation", {}).get("route") == "page-api"
    )
    saved = store.import_observation(text, extract_notes(text, page["source"], page["route"]))
    print(json.dumps(dict(saved, notes=[c["text"] for c in store.inspect(saved["source_id"])["chunks"]]),
                     indent=1, ensure_ascii=False))
