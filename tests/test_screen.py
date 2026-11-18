import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from neurobrain.core import MemoryError, MemoryStore
from neurobrain.extract import extract_notes
from neurobrain.observe import main
from neurobrain.screen import ScreenReader


def response(text, window=9):
    return CompletedProcess(
        [], 0, json.dumps({"text": text, "window_id": window}).encode(), b""
    )


class ScreenTests(unittest.TestCase):
    def test_rejects_changed_window_and_privacy_directive(self):
        reader = ScreenReader("fictional")
        with patch(
            "neurobrain.screen.subprocess.run",
            side_effect=[response("allowed"), response("allowed", 10)],
        ):
            reader.read()
            with self.assertRaises(MemoryError):
                reader.read()
        with patch(
            "neurobrain.screen.subprocess.run",
            return_value=response("neurobrain: do-not-store"),
        ):
            with self.assertRaises(MemoryError):
                ScreenReader("fictional").read()

    def test_screen_to_database_and_changed_focus_rejection(self):
        text = "The fictional demo is on Friday."
        extraction = extract_notes(
            text,
            "fictional",
            "screen-ocr",
            lambda _: {"notes": [{"kind": "milestone", "quote": text}]},
        )
        for status in (0, 1):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                db = root / "observations.sqlite3"
                with (
                    patch(
                        "neurobrain.screen.subprocess.run",
                        side_effect=[
                            response(text),
                            CompletedProcess([], status, b"{}", b""),
                        ],
                    ),
                    patch("neurobrain.extract.extract_notes", return_value=extraction),
                    redirect_stdout(io.StringIO()),
                    redirect_stderr(io.StringIO()),
                ):
                    code = main(
                        [
                            "--screen-title",
                            "fictional",
                            "--save-extracted",
                            "--db",
                            str(db),
                            "--notes-root",
                            str(root),
                        ]
                    )
                self.assertEqual(code, status)
                with MemoryStore(db, root) as store:
                    self.assertEqual(bool(store.search("Friday")), status == 0)
