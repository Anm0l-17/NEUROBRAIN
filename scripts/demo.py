"""Repeatable fictional-data lifecycle demo using a disposable database."""

import json
import tempfile
from pathlib import Path

from neurobrain.core import MemoryError, MemoryStore


def main():
    with tempfile.TemporaryDirectory(prefix="neurobrain-demo-") as temporary:
        base = Path(temporary).resolve()
        notes = base / "notes"
        notes.mkdir()
        project = notes / "project.md"
        project.write_text("# Atlas\nAtlas selected SQLite. DemoForgetCanary.\n")
        retained = notes / "retained.md"
        retained.write_text(
            "Mira prefers concise answers with references. DemoRetainedCanary.\n"
        )
        excluded = notes / "excluded.md"
        excluded.write_text(
            "neurobrain: do-not-store\nNever persist this fictional passage.\n"
        )
        db = base / "memory.sqlite3"
        with MemoryStore(db, notes) as store:
            source = store.import_note(project)
            store.import_note(retained)
            print("1. Imported two fictional notes.")
            assert store.import_note(project)["duplicate"]
            print("2. Duplicate import is idempotent.")
            try:
                store.import_note(excluded)
            except MemoryError:
                print("3. Do-not-store policy blocked a note.")
            else:
                raise AssertionError("Policy failed")
            hits = store.search("SQLite")
            assert hits
            print("4. Retrieved exact evidence:")
            print(json.dumps(hits, indent=2))
            assert store.ask("UnknownZebraCanary")["status"] == "no_evidence"
            print("5. Unsupported query produced no-evidence response.")
            preview = store.preview_forget(source["source_id"])
            print("6. Deletion preview:", json.dumps(preview))
            receipt = store.forget(source["source_id"], preview["preview_token"])
            print("7. Verified deletion receipt:", json.dumps(receipt))
        with MemoryStore(db, notes) as restarted:
            assert not restarted.search("DemoForgetCanary")
            assert restarted.search("DemoRetainedCanary")
            assert project.exists()
            try:
                restarted.import_note(project)
            except MemoryError:
                pass
            else:
                raise AssertionError("Forgotten content was reimported")
            print(
                "8. Restart check passed: target absent, unrelated memory retained, original file intact, reimport blocked."
            )
    print("DEMO PASSED. Temporary memory removed.")


if __name__ == "__main__":
    main()
