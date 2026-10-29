import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from neurobrain.core import MemoryError, MemoryStore


class MemoryLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.base = Path(self.directory.name).resolve()
        self.root = self.base / "notes"
        self.root.mkdir()
        self.db = self.base / "memory.sqlite3"
        self.store = MemoryStore(self.db, self.root)

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def note(self, name="a.md", text="Atlas uses SQLite.\nMira likes references.\n"):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_duplicate_import_and_restart_preserve_evidence(self):
        path = self.note()
        imported = self.store.import_note(path)
        duplicate = self.store.import_note(path)
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(imported["source_id"], duplicate["source_id"])
        self.store.close()
        self.store = MemoryStore(self.db, self.root)
        hit = self.store.search("SQLite")[0]
        self.assertEqual(hit["source_id"], imported["source_id"])
        self.assertEqual(hit["text"], path.read_text())

    def test_long_notes_have_exact_character_and_line_spans(self):
        text = "".join(f"Line {i}: evidence café Atlas\n" for i in range(150))
        result = self.store.import_note(self.note(text=text))
        chunks = self.store.inspect(result["source_id"])["chunks"]
        self.assertGreater(len(chunks), 1)
        self.assertEqual("".join(c["text"] for c in chunks), text)
        for chunk in chunks:
            self.assertEqual(
                text[chunk["char_start"] : chunk["char_end"]], chunk["text"]
            )
            self.assertEqual(
                chunk["line_start"], text.count("\n", 0, chunk["char_start"]) + 1
            )
            self.assertLessEqual(len(chunk["text"]), 1200)

    def test_single_long_line_remains_bounded(self):
        result = self.store.import_note(self.note(text="x" * 3500))
        chunks = self.store.inspect(result["source_id"])["chunks"]
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(c["line_start"] == c["line_end"] == 1 for c in chunks))

    def test_update_keeps_history_but_searches_current_version(self):
        path = self.note(text="The previous database was ObsoleteCanary.\n")
        old = self.store.import_note(path)
        path.write_text("The current database is NewCanary.\n")
        new = self.store.import_note(path)
        self.assertEqual(new["version"], 2)
        self.assertFalse(self.store.search("ObsoleteCanary"))
        self.assertTrue(self.store.search("NewCanary"))
        self.assertIn(
            "ObsoleteCanary", self.store.inspect(old["source_id"])["chunks"][0]["text"]
        )

    def test_delete_all_versions_and_restart_preserves_unrelated_source(self):
        path = self.note(text="ForgetCanary initial decision.\n")
        old = self.store.import_note(path)
        path.write_text("ForgetCanary corrected decision.\n")
        self.store.import_note(path)
        retained = self.note("b.md", "RetainedCanary remains useful.\n")
        self.store.import_note(retained)
        preview = self.store.preview_forget(old["source_id"])
        self.assertEqual(preview["versions"], 2)
        receipt = self.store.forget(old["source_id"], preview["preview_token"])
        self.assertTrue(receipt["verified"])
        self.assertTrue(path.exists())
        self.store.close()
        self.store = MemoryStore(self.db, self.root)
        self.assertFalse(self.store.search("ForgetCanary"))
        self.assertTrue(self.store.search("RetainedCanary"))
        for term in ("ForgetCanary", "corrected", "initial"):
            count = self.store.db.execute(
                "SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH ?", (term,)
            ).fetchone()[0]
            self.assertEqual(count, 0)
        with self.assertRaises(MemoryError):
            self.store.inspect(old["source_id"])
        with self.assertRaises(MemoryError):
            self.store.import_note(path)
        # Copies with identical content also hit the content-hash tombstone.
        with self.assertRaises(MemoryError):
            self.store.import_note(self.note("copy.md", path.read_text()))
        receipt_text = json.dumps(
            dict(self.store.db.execute("SELECT * FROM deletion_receipts").fetchone())
        )
        self.assertNotIn("ForgetCanary", receipt_text)
        self.assertNotIn(str(path), receipt_text)

    def test_stale_preview_refuses_deletion(self):
        path = self.note()
        imported = self.store.import_note(path)
        preview = self.store.preview_forget(imported["source_id"])
        path.write_text("A new version with SQLite.\n")
        self.store.import_note(path)
        with self.assertRaises(MemoryError):
            self.store.forget(imported["source_id"], preview["preview_token"])
        self.assertEqual(len(self.store.sources()), 2)

    def test_import_failure_rolls_back_old_version_and_index(self):
        path = self.note(text="OriginalCanary is retained.")
        old = self.store.import_note(path)
        self.store.db.execute("""CREATE TRIGGER reject_chunk BEFORE INSERT ON chunks
                               BEGIN SELECT RAISE(ABORT,'simulated failure'); END""")
        self.store.db.commit()
        path.write_text("NewCanary should never persist.")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.import_note(path)
        self.assertEqual(self.store.sources()[0]["id"], old["source_id"])
        self.assertTrue(self.store.search("OriginalCanary"))
        self.assertFalse(self.store.search("NewCanary"))

    def test_delete_failure_rolls_back_receipts_tombstones_and_evidence(self):
        imported = self.store.import_note(self.note())
        self.store.db.execute("""CREATE TRIGGER reject_receipt BEFORE INSERT ON deletion_receipts
                               BEGIN SELECT RAISE(ABORT,'simulated failure'); END""")
        self.store.db.commit()
        preview = self.store.preview_forget(imported["source_id"])
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.forget(imported["source_id"], preview["preview_token"])
        self.assertTrue(self.store.search("SQLite"))
        self.assertEqual(
            self.store.db.execute("SELECT count(*) FROM tombstones").fetchone()[0], 0
        )

    def test_policy_rejections_persist_no_source_text(self):
        cases = [
            ("a.pdf", "Not supported"),
            ("empty.txt", "  "),
            ("binary.md", "\x00private"),
            ("secret.md", "password = fictional-secret"),
            ("denied.md", "neurobrain: do-not-store\nPrivateCanary"),
            (".hidden.md", "HiddenCanary"),
            ("large.md", "x" * 1_048_577),
        ]
        for name, text in cases:
            with self.subTest(name=name), self.assertRaises(MemoryError):
                self.store.import_note(self.note(name, text))
        bad = self.root / "bad.md"
        bad.write_bytes(b"\xff\xfe")
        with self.assertRaises(MemoryError):
            self.store.import_note(bad)
        with self.assertRaises(MemoryError):
            self.store.import_note(self.root / "missing.md")
        self.assertEqual(self.store.sources(), [])
        self.assertEqual(
            self.store.db.execute("SELECT count(*) FROM chunks").fetchone()[0], 0
        )

    def test_outside_root_and_symlink_are_rejected(self):
        outside = self.base / "outside.md"
        outside.write_text("OutsideCanary")
        with self.assertRaises(MemoryError):
            self.store.import_note(outside)
        link = self.root / "link.md"
        link.symlink_to(outside)
        with self.assertRaises(MemoryError):
            self.store.import_note(link)

    def test_query_scope_filters_previously_imported_notes(self):
        self.store.import_note(self.note())
        nested = self.root / "other"
        nested.mkdir()
        with MemoryStore(self.db, nested) as restricted:
            self.assertEqual(restricted.sources(), [])
            self.assertEqual(restricted.search("SQLite"), [])

    def test_search_treats_special_syntax_as_literal_tokens(self):
        self.store.import_note(self.note())
        for query in ('"', "*", "NOT", "SQLite OR (", "'; DROP TABLE sources; --"):
            self.store.search(query)
        self.assertEqual(len(self.store.sources()), 1)
        self.assertEqual(self.store.ask("UnseenCanary")["status"], "no_evidence")
        self.assertEqual(self.store.ask("SQLite")["mode"], "extractive")

    def test_foreign_keys_and_fts_integrity(self):
        self.store.import_note(self.note())
        self.assertEqual(self.store.db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        self.assertEqual(
            self.store.db.execute("PRAGMA foreign_key_check").fetchall(), []
        )
        self.store.db.execute(
            "INSERT INTO chunks_fts(chunks_fts,rank) VALUES('integrity-check',1)"
        )


if __name__ == "__main__":
    unittest.main()
