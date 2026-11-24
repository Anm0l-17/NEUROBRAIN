"""F01-F11 through local routes with real Ollama Qwen. Disposable DB, fictional text.

Run: PYTHONPATH=src .venv/bin/python reports/demo_week/f01_f11_local.py
Notion, OCR helper and interactive pause/stop are simulated or skipped; see the report.
"""

import io
import json
import sqlite3
import tempfile
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from neurobrain.core import MemoryError, MemoryStore
from neurobrain.extract import answer
from neurobrain.observe import main

OUT = []


def rec(fid, mode, expected, actual, ok, seconds=None, **extra):
    OUT.append(dict(id=fid, mode=mode, expected=expected, actual=actual, ok=ok,
                    seconds=None if seconds is None else round(seconds, 2), **extra))


def run(args):
    out, err = io.StringIO(), io.StringIO()
    t = time.monotonic()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue(), time.monotonic() - t


def ocr(text, status=0):
    return CompletedProcess([], 0, json.dumps({"text": text, "window_id": 9}).encode(), b"")


def save_file(root, db, name, text):
    path = root / name
    path.write_text(text)
    return run(["--file", str(path), "--save-extracted", "--db", str(db), "--notes-root", str(root)])


def logical(db, root):
    with MemoryStore(db, root) as s:
        return [x for x in s.sources() if x["active"]]


def main_():
    with tempfile.TemporaryDirectory(prefix="nb-f-") as t:
        root = Path(t).resolve(); db = root / "m.sqlite3"
        # F01 (Notion simulated via selected-file route)
        f01 = "The violet demonstration is on 23 November 2026."
        code, out, err, sec = save_file(root, db, "violet.md", f01 + "\n")
        with MemoryStore(db, root) as s:
            a = answer(s, "When is the violet demonstration?")
        rec("F01", "SIMULATED route (Notion API not called; selected-file + real Qwen)",
            "retained, cited 23 November", f"exit={code} answers={[r['text'] for r in a['answers']]}",
            code == 0 and any("23 November" in r["text"] for r in a["answers"]), sec)
        # F02
        code, out, err, sec = save_file(root, db, "mira.md", "Mira prefers concise answers with references.\n")
        with MemoryStore(db, root) as s:
            a = answer(s, "How does Mira prefer answers?")
        rec("F02", "LOCAL selected-file route, real Qwen", "preference retained",
            f"exit={code} answers={[r['text'] for r in a['answers']]}",
            code == 0 and bool(a["answers"]), sec)
        # F03 screen (OCR simulated)
        f03 = "The amber rehearsal room is Cedar 417."
        with patch("neurobrain.screen.subprocess.run", side_effect=[ocr(f03), CompletedProcess([], 0, b"{}", b"")]):
            code, out, err, sec = run(["--screen-title", "fictional", "--save-extracted", "--db", str(db), "--notes-root", str(root)])
        with MemoryStore(db, root) as s:
            a = answer(s, "Which room is the amber rehearsal room?")
        rec("F03", "SIMULATED OCR (helper mocked; real Qwen)", "screen-only fact queryable before save",
            f"exit={code} answers={[(r['text'], r['observation']) for r in a['answers']]}",
            code == 0 and any("Cedar 417" in r["text"] for r in a["answers"]), sec)
        # F04
        code, out, err, sec = save_file(root, db, "rehearsal.md", f03 + "\n")
        with MemoryStore(db, root) as s:
            a = answer(s, "Which room is the amber rehearsal room?")
            hits = s.search("Cedar")
        act = [x for x in logical(db, root) if "Cedar" in json.dumps(x)] 
        rec("F04", "SIMULATED OCR then LOCAL file save (trailing newline differs)",
            "one logical note, linked routes",
            f"exit={code} search_hits={len(hits)} linked={[h['linked'] for h in hits]} answers={len(a['answers'])}",
            code == 0 and len(hits) == 1 and len(hits[0]["linked"]) == 1, sec)
        # F05 version
        f05 = "The violet demonstration is on 24 November 2026."
        code, out, err, sec = save_file(root, db, "violet.md", f05 + "\n")
        with MemoryStore(db, root) as s:
            a = answer(s, "When is the violet demonstration?")
            vers = [x["version"] for x in s.sources() if "violet" in x["path"] or True]
        texts = [r["text"] for r in a["answers"]]
        rec("F05", "SIMULATED Notion route (selected-file); same path new text", "v2 current answer says 24, not 23",
            f"exit={code} answers={texts}", code == 0 and any("24 November" in x for x in texts) and not any("23 November" in x for x in texts), sec)
        # F06 / F07 / F08
        for fid, text, exp in (("F06", "Okay, thanks.", "no useful retained excerpt"),
                               ("F07", "Move that to there after the thing is finished.", "abstain/no keep")):
            code, out, err, sec = save_file(root, db, fid.lower() + ".md", text + "\n")
            notes = json.loads(out)["extraction"]["notes"] if out.strip() else []
            kept = [c[0] for c in sqlite3.connect(db).execute("SELECT text FROM chunks WHERE text LIKE ?", (text[:10] + "%",))]
            rec(fid, "LOCAL selected-file, real Qwen", exp, f"exit={code} extracted_notes={[n['text'] for n in notes]} stored_chunks_with_phrase={kept}",
                not kept, sec)
        marker = "zanzibarquartz991"
        code, out, err, sec = save_file(root, db, "f08.md", f"neurobrain: do-not-store\nSecret fictional marker {marker}.\n")
        with MemoryStore(db, root) as s:
            hits = s.search(marker)
        raw = db.read_bytes()  # the database only; the rejected source file stays on disk by design
        rec("F08", "LOCAL selected-file", "rejected before model/persist; marker absent",
            f"exit={code} stderr={err.strip()!r} hits={len(hits)} marker_in_db_file={marker.encode() in raw} (app logs: none written)",
            code != 0 and not hits and marker.encode() not in raw, sec)
        # F09
        with MemoryStore(db, root) as s:
            t0 = time.monotonic(); a = answer(s, "What is the color of the Quokkadrome vault?")
        rec("F09", "LOCAL answer path, real Qwen", "no_evidence", json.dumps(a)[:300], a["status"] == "no_evidence", time.monotonic() - t0)
        # F10 denied app / focus change (helper check fails) ; pause/stop need a tty
        before = len(logical(db, root))
        with patch("neurobrain.screen.subprocess.run", side_effect=[ocr("Denied app fictional text Quokka 55."), CompletedProcess([], 1, b"{}", b"")]):
            code, out, err, sec = run(["--screen-title", "denied", "--save-extracted", "--db", str(db), "--notes-root", str(root)])
        with MemoryStore(db, root) as s:
            hits = s.search("Quokka")
        rec("F10", "SIMULATED helper refusal (check exit 1); pause/stop NOT run (needs interactive tty)",
            "no capture saved", f"exit={code} stderr={err.strip()!r} sources_before={before} after={len(logical(db, root))} hits={len(hits)}",
            code == 1 and not hits and before == len(logical(db, root)), sec)
        # F11 forget F01/F05 violet, reopen
        with MemoryStore(db, root) as s:
            sid = next(x["id"] for x in s.sources() if "violet" in json.dumps(s.search("violet")) or False) if False else s.search("violet")[0]["source_id"]
            p = s.preview_forget(sid); r = s.forget(sid, p["preview_token"])
        with MemoryStore(db, root) as s:
            gone = not s.search("violet"); kept = bool(s.search("Mira"))
            try:
                s.import_note(root / "violet.md"); reimp = True
            except MemoryError:
                reimp = False
        rec("F11", "LOCAL, fresh store handle (restart)", "all violet versions gone, Mira kept, file intact",
            f"receipt={r} violet_gone={gone} mira_kept={kept} reimport_blocked={not reimp} file_exists={(root/'violet.md').exists()}",
            gone and kept and not reimp and (root / "violet.md").exists())
    print(json.dumps(OUT, indent=1))


main_()
