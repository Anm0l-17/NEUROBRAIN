"""Live local-Qwen evidence walkthrough; fictional inputs and a disposable database."""

import json
import tempfile
import time
from pathlib import Path

from neurobrain.core import MemoryError, MemoryStore
from neurobrain.extract import answer, extract_notes


def main():
    started = time.monotonic()
    checks = []
    with tempfile.TemporaryDirectory(prefix="neurobrain-observation-demo-") as temp:
        root = Path(temp)
        db = root / "memory.sqlite3"
        original = "The violet prototype demonstration is on 23 November 2026."
        updated = "The violet prototype demonstration is on 24 November 2026."
        retained = "Mira prefers concise answers with references."
        question = "When is the violet prototype demonstration?"

        def capture(text, source):
            before = time.monotonic()
            extracted = extract_notes(text, source, "selected-file")
            assert extracted["notes"], "Model omitted the fictional useful note"
            with MemoryStore(db, root) as store:
                result = store.import_observation(text, extracted)
            checks.append(
                {
                    "check": "extract_save",
                    "source": source,
                    "seconds": round(time.monotonic() - before, 3),
                    **result,
                }
            )
            return extracted, result

        extracted, first = capture(original, "fictional-demo")
        capture(retained, "fictional-preference")
        with MemoryStore(db, root) as store:
            assert store.import_observation(original, extracted)["duplicate"]
            reply = answer(store, question)
            assert any("23 November 2026" in row["text"] for row in reply["answers"])
            assert answer(store, "UnknownZebraCanary")["status"] == "no_evidence"
            checks.append(
                {"check": "restart_citation_duplicate_no_evidence", "answer": reply}
            )

        _, second = capture(updated, "fictional-demo")
        assert second["version"] == 2
        with MemoryStore(db, root) as store:
            reply = answer(store, question)
            assert any("24 November 2026" in row["text"] for row in reply["answers"])
            assert all(
                "23 November 2026" not in row["text"] for row in reply["answers"]
            )
            preview = store.preview_forget(first["source_id"])
            receipt = store.forget(first["source_id"], preview["preview_token"])
            assert receipt["verified"] and receipt["removed_versions"] == 2
            checks.append(
                {"check": "updated_answer_and_all_version_forget", "receipt": receipt}
            )

        with MemoryStore(db, root) as store:
            assert answer(store, question)["status"] == "no_evidence"
            assert store.search("Mira")
            try:
                store.import_observation(original, extracted)
            except MemoryError:
                pass
            else:
                raise AssertionError("Forgotten content reimported")
        try:
            extract_notes(
                "neurobrain: do-not-store\nFictional private marker.",
                "blocked",
                "selected-file",
            )
        except MemoryError:
            pass
        else:
            raise AssertionError("Privacy directive accepted")
        checks.append(
            {"check": "restart_deletion_retention_tombstone_privacy", "passed": True}
        )
    print(
        json.dumps(
            {
                "passed": True,
                "scope": "fictional local model smoke; not quality benchmark",
                "seconds": round(time.monotonic() - started, 3),
                "temporary_database_removed": True,
                "checks": checks,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
