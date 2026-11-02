import tempfile
import unittest
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.semantic import SemanticIndex, hybrid_search, load_encoder
from scripts.evaluate_semantic import ENCODER, REVISION, load_cases, run

MODEL, MODEL_ERROR = load_encoder()
MODEL_AVAILABLE = MODEL is not None


@unittest.skipUnless(MODEL_AVAILABLE, "Pinned semantic model is unavailable locally")
class SemanticModelTests(unittest.TestCase):
    def test_offline_semantic_experiment_returns_finite_scores(self):
        path = Path(__file__).parents[1] / "data/semantic_evaluation_v0.jsonl"
        result = run(load_cases(path))
        self.assertEqual(result["encoder"], ENCODER)
        self.assertEqual(result["revision"], REVISION)
        self.assertEqual(result["semantic_recall_at_5"], 1.0)
        self.assertTrue(result["semantic_available"])

    def test_rebuild_after_restart_excludes_forgotten_source(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            notes = base / "notes"
            notes.mkdir()
            note = notes / "forget.md"
            note.write_text("ForgetSemanticCanary is stored.", encoding="utf-8")
            db = base / "memory.sqlite3"
            encoder = MODEL
            with MemoryStore(db, notes) as store:
                imported = store.import_note(note)
                index = SemanticIndex(store, encoder)
                index.rebuild()
                self.assertTrue(index.search("ForgetSemanticCanary"))
                hits, mode = hybrid_search(store, "ForgetSemanticCanary", encoder)
                self.assertEqual(mode, "hybrid-rrf")
                self.assertTrue(hits)
                preview = store.preview_forget(imported["source_id"])
                store.forget(imported["source_id"], preview["preview_token"])
                self.assertEqual(
                    hybrid_search(store, "ForgetSemanticCanary", encoder)[0], []
                )
            with MemoryStore(db, notes) as restarted:
                index = SemanticIndex(restarted, encoder)
                index.rebuild()
                self.assertEqual(index.search("ForgetSemanticCanary"), [])


class SemanticFallbackTests(unittest.TestCase):
    def test_hybrid_search_has_explicit_lexical_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            notes = base / "notes"
            notes.mkdir()
            note = notes / "fallback.md"
            note.write_text("FallbackCanary uses SQLite.", encoding="utf-8")
            with MemoryStore(base / "memory.sqlite3", notes) as store:
                store.import_note(note)
                hits, mode = hybrid_search(store, "FallbackCanary", None)
                self.assertEqual(mode, "lexical-fallback")
                self.assertEqual(
                    hits[0]["citation"].split(":")[0], hits[0]["source_id"]
                )


if __name__ == "__main__":
    unittest.main()
