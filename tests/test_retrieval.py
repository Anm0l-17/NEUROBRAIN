import sqlite3
import tempfile
import unittest
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.extract import answer, extract_notes

PAGE = (
    "Priya stepped back as organizer in March and handed book selection to Daniel. "
    "Parking is free on the street after 6 pm. "
    "The current book is no longer The Glass Orchard. "
    "The group dropped it halfway through and switched to Salt and Signal."
)
NOTES = [
    "Priya stepped back as organizer in March and handed book selection to Daniel.",
    "Parking is free on the street after 6 pm.",
    "The current book is no longer The Glass Orchard.",
    "The group dropped it halfway through and switched to Salt and Signal.",
]


def save_page(store, text=PAGE, notes=NOTES):
    quotes = [{"kind": "fact", "quote": n} for n in notes]
    return store.import_observation(
        text, extract_notes(text, "book-club", "page-api", lambda _: {"notes": quotes})
    )


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name).resolve()
        self.db = self.root / "memory.sqlite3"
        self.store = MemoryStore(self.db, self.root)

    def tearDown(self):
        self.store.close()
        self.directory.cleanup()

    def texts(self, query):
        return [r["text"] for r in self.store.search(query)]

    def test_plural_question_finds_singular_note_and_skips_question_words(self):
        save_page(self.store)
        self.assertIn(NOTES[0], self.texts("Who picks the books?"))
        # "is"/"the" alone used to pull in every note; parking shares no content word.
        self.assertNotIn(NOTES[1], self.texts("Who picks the books?"))

    def test_all_stopword_query_falls_back_to_its_words(self):
        save_page(self.store)
        self.assertIn(NOTES[1], self.texts("is the"))

    def test_top_note_brings_its_next_note_from_the_same_page(self):
        save_page(self.store)
        found = self.texts("What is the current book?")
        self.assertEqual(found[0], NOTES[2])
        self.assertIn(NOTES[3], found)
        one = self.store.search("What is the current book?", limit=1)
        self.assertEqual([r["text"] for r in one], [NOTES[2]])

    def test_next_note_takes_the_last_slot_when_results_are_full(self):
        save_page(self.store)
        found = self.store.search("current book Daniel parking", limit=2)
        self.assertEqual([r["text"] for r in found], [NOTES[2], NOTES[3]])
        self.assertEqual(found[1]["citation"], f"{found[1]['source_id']}:{found[1]['id']}")
        self.assertEqual(found[1]["observation"], found[0]["observation"])

    def test_next_note_comes_only_from_the_current_version(self):
        save_page(self.store)
        save_page(self.store, notes=NOTES[:3])
        self.assertNotIn(NOTES[3], self.texts("What is the current book?"))

    def test_forgotten_page_leaves_no_next_note(self):
        saved = save_page(self.store)
        preview = self.store.preview_forget(saved["source_id"])
        self.store.forget(saved["source_id"], preview["preview_token"])
        self.assertEqual(self.texts("What is the current book?"), [])

    def test_plain_file_passages_get_no_next_note(self):
        note = self.root / "a.md"
        note.write_text("The current book is short.\n" + "x " * 700 + "\nSalt.\n")
        self.store.import_note(note)
        self.assertEqual(len(self.store.search("current book")), 1)

    def test_answer_recheck_keeps_the_next_note(self):
        save_page(self.store)

        def requester(payload):
            evidence = self.store.search("What is the current book?")
            return {"citations": [r["citation"] for r in evidence if r["text"] == NOTES[3]]}

        result = answer(self.store, "What is the current book?", requester)
        self.assertEqual([a["text"] for a in result["answers"]], [NOTES[3]])

    def test_old_unstemmed_index_is_rebuilt_on_open(self):
        save_page(self.store)
        self.store.close()
        db = sqlite3.connect(self.db)
        db.executescript(
            "DROP TABLE chunks_fts;"
            "CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='id');"
            "INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild');"
        )
        db.close()
        self.store = MemoryStore(self.db, self.root)
        self.assertIn(NOTES[0], self.texts("Who picks the books?"))
        self.assertEqual(self.store.db.execute("PRAGMA user_version").fetchone()[0], 1)
        with self.store.db:
            self.store.db.execute(
                "INSERT INTO chunks_fts(chunks_fts,rank) VALUES('integrity-check',1)"
            )
        saved = save_page(self.store, notes=NOTES[:2])
        self.assertNotIn(NOTES[3], self.texts("What is the current book?"))
        preview = self.store.preview_forget(saved["source_id"])
        self.store.forget(saved["source_id"], preview["preview_token"])
        self.assertEqual(self.texts("Daniel"), [])


if __name__ == "__main__":
    unittest.main()
