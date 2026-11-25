import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from neurobrain.core import MemoryError, MemoryStore
from neurobrain.extract import answer, extract_notes


class ExtractionTests(unittest.TestCase):
    def test_empty_current_snapshot_hides_old_evidence_without_erasing_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with MemoryStore(root / "memory.sqlite3", root) as store:
                text = "The meeting is on Friday."
                old = store.import_observation(
                    text,
                    extract_notes(
                        text,
                        "fixture",
                        "page-api",
                        lambda _: {"notes": [{"kind": "fact", "quote": text}]},
                    ),
                )
                text = "Okay, thanks."
                new = store.import_observation(
                    text,
                    extract_notes(text, "fixture", "page-api", lambda _: {"notes": []}),
                )
                self.assertEqual(new["chunks"], 0)
                self.assertEqual(new["version"], 2)
                self.assertFalse(store.search("Friday"))
                self.assertEqual(len(store.inspect(old["source_id"])["chunks"]), 1)

    def test_changed_extraction_versions_unchanged_source_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = "The meeting is on Friday. The demo is on Saturday."
            with MemoryStore(root / "memory.sqlite3", root) as store:

                def extraction(quote):
                    return extract_notes(
                        text,
                        "fixture",
                        "page-api",
                        lambda _: {"notes": [{"kind": "fact", "quote": quote}]},
                    )

                first = extraction("The meeting is on Friday.")
                store.import_observation(text, first)
                second = extraction("The demo is on Saturday.")
                saved = store.import_observation(text, second)
                self.assertEqual(saved["version"], 2)
                listed = next(
                    r for r in store.sources() if r["id"] == saved["source_id"]
                )
                self.assertEqual(
                    listed["observation"], {"source": "fixture", "route": "page-api"}
                )
                self.assertNotIn("metadata", listed)
                self.assertFalse(store.search("Friday"))
                self.assertTrue(store.search("Saturday"))
                self.assertEqual(
                    store.search("Saturday")[0]["observation"], listed["observation"]
                )
                self.assertTrue(store.import_observation(text, second)["duplicate"])
                preview = store.preview_forget(saved["source_id"])
                receipt = store.forget(saved["source_id"], preview["preview_token"])
                self.assertEqual(receipt["removed_versions"], 2)

    def test_answer_constrains_citations_and_rechecks_concurrent_forgetting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            note = root / "note.md"
            note.write_text("The fictional meeting is on Saturday.")
            with MemoryStore(root / "memory.sqlite3", root) as store:
                source = store.import_note(note)
                citation = store.search("Saturday")[0]["citation"]

                def requester(payload):
                    self.assertEqual(
                        payload["format"]["properties"]["citations"]["items"]["enum"],
                        [citation],
                    )
                    preview = store.preview_forget(source["source_id"])
                    store.forget(source["source_id"], preview["preview_token"])
                    return {"citations": [citation]}

                self.assertEqual(
                    answer(store, "Saturday", requester),
                    {"status": "no_evidence", "answers": []},
                )

    def test_answer_selector_model_comes_from_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            note = root / "note.md"
            note.write_text("The fictional meeting is on Saturday.")
            with MemoryStore(root / "memory.sqlite3", root) as store:
                store.import_note(note)
                seen = []

                def requester(payload):
                    seen.append(payload["model"])
                    return {"citations": []}

                with patch.dict(os.environ, {"NEUROBRAIN_SELECTOR_MODEL": "neurobrain-selector-v2"}):
                    answer(store, "Saturday", requester)
                with patch.dict(os.environ, {"NEUROBRAIN_SELECTOR_MODEL": ""}):
                    answer(store, "Saturday", requester)
                self.assertEqual(seen, ["neurobrain-selector-v2", "qwen3.5:4b"])

    def test_forget_removes_plain_and_extracted_copies_of_same_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            note = root / "plan.md"
            text = "The fictional launch moved to Thursday."
            note.write_text(text)
            with MemoryStore(root / "memory.sqlite3", root) as store:
                plain = store.import_note(note)
                extraction = extract_notes(
                    text,
                    str(note),
                    "selected-file",
                    lambda _: {"notes": [{"kind": "decision", "quote": text}]},
                )
                store.import_observation(text, extraction)
                found = store.search("Thursday")
                self.assertEqual(len(found), 1)
                self.assertEqual(len(found[0]["linked"]), 1)
                preview = store.preview_forget(plain["source_id"])
                receipt = store.forget(plain["source_id"], preview["preview_token"])
                self.assertEqual(receipt["removed_versions"], 2)
                self.assertFalse(store.search("Thursday"))
                with self.assertRaises(MemoryError):
                    store.import_note(note)
                with self.assertRaises(MemoryError):
                    store.import_observation(text, extraction)

    def test_forget_keeps_linked_copy_versions_with_different_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            note = root / "plan.md"
            text = "The fictional launch moved to Thursday."
            note.write_text(text)
            with MemoryStore(root / "memory.sqlite3", root) as store:
                plain = store.import_note(note)

                def extraction(body):
                    return extract_notes(
                        body,
                        "screen-window",
                        "screen-ocr",
                        lambda _: {"notes": [{"kind": "fact", "quote": body}]},
                    )

                store.import_observation(text, extraction(text))
                later = "The fictional budget review is on Monday."
                store.import_observation(later, extraction(later))
                preview = store.preview_forget(plain["source_id"])
                receipt = store.forget(plain["source_id"], preview["preview_token"])
                self.assertEqual(receipt["removed_versions"], 2)
                self.assertFalse(store.search("Thursday"))
                self.assertTrue(store.search("Monday"))

    def test_forgetting_a_capture_also_takes_a_plain_copy_of_a_sibling_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            note = root / "plan.md"
            b_text = "The amber rehearsal room is Cedar 417."
            note.write_text(b_text)

            def capture(body):
                return extract_notes(
                    body,
                    "window",
                    "screen-ocr",
                    lambda _: {"notes": [{"kind": "fact", "quote": body}]},
                )

            with MemoryStore(root / "memory.sqlite3", root) as store:
                a_text = "The violet demonstration is on 23 November."
                a = store.import_observation(a_text, capture(a_text))
                store.import_observation(b_text, capture(b_text))
                store.import_note(note)
                preview = store.preview_forget(a["source_id"])
                self.assertEqual(preview["versions"], 3)
                store.forget(a["source_id"], preview["preview_token"])
                self.assertFalse(store.search("Cedar"))

    def test_forget_keeps_note_sharing_only_one_short_quote(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            def save(store, name, quotes):
                body = "\n".join(quotes) + "\n"
                extraction = extract_notes(
                    body,
                    name,
                    "selected-file",
                    lambda _: {"notes": [{"kind": "fact", "quote": q} for q in quotes]},
                )
                return store.import_observation(body, extraction)

            with MemoryStore(root / "memory.sqlite3", root) as store:
                trip = save(store, "trip", ["Trip to Pune.", "Approved."])
                save(store, "budget", ["Budget for Q4 is 2 lakh.", "Approved."])
                preview = store.preview_forget(trip["source_id"])
                self.assertEqual(preview["versions"], 1)
                store.forget(trip["source_id"], preview["preview_token"])
                self.assertTrue(store.search("lakh"))

    def test_unresolved_reference_quotes_are_dropped_not_stored(self):
        text = "Move that to there after the thing is finished.\nMira booked it for Friday."
        out = extract_notes(
            text,
            "f07",
            "selected-file",
            lambda _: {
                "notes": [
                    {
                        "kind": "decision",
                        "quote": "Move that to there after the thing is finished.",
                    },
                    {"kind": "fact", "quote": "Mira booked it for Friday."},
                ]
            },
        )
        self.assertEqual(
            [n["text"] for n in out["notes"]], ["Mira booked it for Friday."]
        )

    def test_lone_short_notes_do_not_link_distinct_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            def save(store, name, body):
                extraction = extract_notes(
                    body,
                    name,
                    "selected-file",
                    lambda _: {"notes": [{"kind": "fact", "quote": body}]},
                )
                return store.import_observation(body, extraction)

            with MemoryStore(root / "memory.sqlite3", root) as store:
                one = save(store, "trip", "Approved.")
                save(store, "budget", "Approved.!")
                self.assertEqual(store.preview_forget(one["source_id"])["versions"], 1)

    def test_forgotten_term_is_absent_from_database_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            db = root / "memory.sqlite3"
            for name, text in (
                ("keep.md", "Mira likes tea."),
                ("gone.md", "Zqxmarkerwvu is fictional."),
            ):
                (root / name).write_text(text)
            with MemoryStore(db, root) as store:
                store.import_note(root / "keep.md")
                gone = store.import_note(root / "gone.md")["source_id"]
                preview = store.preview_forget(gone)
                store.forget(gone, preview["preview_token"])
            raw = db.read_bytes().lower()
            self.assertNotIn(b"zqxmarkerwvu", raw)
            self.assertIn(b"mira", raw)

    def test_forgetting_current_text_does_not_bring_back_an_outdated_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            v1 = "The violet demonstration is on 23 November 2026."
            v2 = "The violet demonstration is on 24 November 2026."

            def page(text):
                return extract_notes(
                    text,
                    "demo-page",
                    "page-api",
                    lambda _: {"notes": [{"kind": "milestone", "quote": text}]},
                )

            copy = root / "copy.md"
            copy.write_text(v2)
            with MemoryStore(root / "memory.sqlite3", root) as store:
                store.import_observation(v1, page(v1))
                store.import_observation(v2, page(v2))
                plain = store.import_note(copy)
                self.assertIn(
                    "24 November", store.search("violet demonstration")[0]["text"]
                )
                preview = store.preview_forget(plain["source_id"])
                store.forget(plain["source_id"], preview["preview_token"])
                self.assertEqual(store.search("violet demonstration"), [])
                # The old text is not tombstoned: importing it again makes a new current version.
                again = store.import_observation(v1, page(v1))
                self.assertFalse(again["duplicate"])
                self.assertIn(
                    "23 November", store.search("violet demonstration")[0]["text"]
                )

    def test_screen_captures_are_separate_sources_and_forget_together(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            def capture(body):
                return extract_notes(
                    body,
                    "window",
                    "screen-ocr",
                    lambda _: {"notes": [{"kind": "fact", "quote": body}]},
                )

            first = "The amber rehearsal room is Cedar 417."
            second = "The violet demonstration is on 23 November."
            with MemoryStore(root / "memory.sqlite3", root) as store:
                a = store.import_observation(first, capture(first))
                b = store.import_observation(second, capture(second))
                self.assertNotEqual(a["source_id"], b["source_id"])
                self.assertTrue(
                    store.import_observation(first, capture(first))["duplicate"]
                )
                self.assertTrue(store.search("Cedar"))
                self.assertTrue(store.search("violet"))
                preview = store.preview_forget(a["source_id"])
                self.assertEqual(preview["versions"], 2)
                store.forget(a["source_id"], preview["preview_token"])
                self.assertFalse(store.search("Cedar"))
                self.assertFalse(store.search("violet"))

    def test_unsaved_screen_fact_then_saved_file_is_one_logical_note(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            ocr = "The amber rehearsal room is Cedar 417."
            saved = root / "rehearsal.md"
            saved.write_text(ocr + "\n")  # file bytes differ from OCR text
            with MemoryStore(root / "memory.sqlite3", root) as store:
                screen = extract_notes(
                    ocr,
                    "window",
                    "screen-ocr",
                    lambda _: {"notes": [{"kind": "fact", "quote": ocr}]},
                )
                a = store.import_observation(ocr, screen)
                body = saved.read_text()
                file = extract_notes(
                    body,
                    str(saved),
                    "selected-file",
                    lambda _: {"notes": [{"kind": "fact", "quote": ocr}]},
                )
                b = store.import_observation(body, file)
                self.assertNotEqual(a["source_id"], b["source_id"])
                found = store.search("Cedar")
                self.assertEqual(len(found), 1)
                self.assertEqual(len(found[0]["linked"]), 1)
                active = [s for s in store.sources() if s["active"]]
                self.assertEqual(len(active), 1)
                self.assertEqual(len(active[0]["linked"]), 1)
                preview = store.preview_forget(b["source_id"])
                self.assertEqual(preview["versions"], 2)
                store.forget(b["source_id"], preview["preview_token"])
                self.assertFalse(store.search("Cedar"))
                self.assertFalse(store.sources())

    def test_storage_updates_restart_forgetting_and_citations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = root / "memory.sqlite3"

            def observation(text):
                return extract_notes(
                    text,
                    "demo-page",
                    "page-api",
                    lambda _: {"notes": [{"kind": "fact", "quote": text}]},
                )

            with MemoryStore(db, root) as store:
                text = "The meeting is on Friday."
                extraction = observation(text)
                first = store.import_observation(text, extraction)
                self.assertTrue(store.import_observation(text, extraction)["duplicate"])
                updated = "The meeting is on Saturday."
                second = store.import_observation(updated, observation(updated))
                self.assertEqual(second["version"], 2)
                self.assertFalse(store.search("Friday"))
            with MemoryStore(db, root) as store:
                citation = store.search("Saturday")[0]["citation"]
                result = answer(store, "Saturday", lambda _: {"citations": [citation]})
                self.assertEqual(result["answers"][0]["text"], updated)
                with self.assertRaises(MemoryError):
                    answer(store, "Saturday", lambda _: {"citations": ["invented"]})
                self.assertIsNotNone(store.inspect(second["source_id"])["observation"])
                preview = store.preview_forget(first["source_id"])
                store.forget(first["source_id"], preview["preview_token"])
                self.assertEqual(
                    store.db.execute(
                        "SELECT count(*) FROM observation_metadata"
                    ).fetchone()[0],
                    0,
                )
            with MemoryStore(db, root) as store:
                self.assertFalse(store.search("Saturday"))
                with self.assertRaises(MemoryError):
                    store.import_observation(text, extraction)

    def test_evidence_offsets_and_duplicate_suppression(self):
        quote = "The demo is on Friday."
        note = dict(kind="milestone", quote=quote)
        result = extract_notes(
            "Title\n" + quote, "fixture", "screen", lambda _: {"notes": [note, note]}
        )
        self.assertEqual(len(result["notes"]), 1)
        self.assertEqual(result["notes"][0]["char_start"], 6)
        self.assertEqual(result["notes"][0]["line_start"], 2)

    def test_privacy_precedes_inference(self):
        generator = Mock()
        with self.assertRaises(MemoryError):
            extract_notes("neurobrain: do-not-store", "fixture", "screen", generator)
        generator.assert_not_called()

    def test_invented_evidence_and_malformed_response_rejected(self):
        for result in (
            {},
            {"notes": None},
            {"notes": [{"kind": "fact", "quote": "invented"}]},
        ):
            with self.subTest(result=result), self.assertRaises(MemoryError):
                extract_notes("actual", "fixture", "screen", lambda _, r=result: r)
