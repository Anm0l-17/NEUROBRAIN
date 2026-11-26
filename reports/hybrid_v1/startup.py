"""Cost of the hybrid in a fresh process, and whether its index sees another process's save.

PYTHONPATH=src python reports/hybrid_v1/startup.py COPY.sqlite3 NOTES_ROOT
Writes one note into the copy, so never point it at the live database.
"""

import json
import resource
import subprocess
import sys
import time

t0 = time.perf_counter()
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.semantic import hybrid_search, load_encoder

db, root = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
if db.name == "observations.sqlite3":
    sys.exit("Use a scratch copy, never the live database.")
imported = time.perf_counter()
before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
encoder, error = load_encoder()
if encoder is None:
    sys.exit(error)
loaded = time.perf_counter()
SAVE = """
import sys
from pathlib import Path
from neurobrain.core import MemoryStore
from neurobrain.extract import extract_notes
text = "The ZebraCanary rehearsal is in Hall Q."
with MemoryStore(Path(sys.argv[1]), Path(sys.argv[2])) as store:
    store.import_observation(text, extract_notes(
        text, "startup-check", "page-api", lambda _: {"notes": [{"kind": "fact", "quote": text}]}))
"""
with MemoryStore(db, root) as store:
    times = []
    for _ in range(3):
        t = time.perf_counter()
        hybrid_search(store, "Why did the venue change?", encoder)
        times.append(time.perf_counter() - t)
    subprocess.run([sys.executable, "-c", SAVE, str(db), str(root)], check=True)
    seen = any("ZebraCanary" in h["text"]
               for h in hybrid_search(store, "Where is the ZebraCanary rehearsal?", encoder)[0])
    notes = store.db.execute("SELECT count(*) FROM chunks").fetchone()[0]
# ru_maxrss is bytes on macOS.
after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(json.dumps(dict(
    lexical_imports_s=round(imported - t0, 2), torch_and_encoder_load_s=round(loaded - imported, 2),
    first_query_with_index_build_s=round(times[0], 3), later_query_s=round(min(times[1:]), 3),
    peak_rss_mb_before=round(before / 1e6), peak_rss_mb_after=round(after / 1e6),
    chunks=notes, sees_other_process_save=seen), indent=1))
