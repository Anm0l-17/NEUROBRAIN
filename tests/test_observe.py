import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from neurobrain import observe


class ObservationTests(unittest.TestCase):
    def test_selected_saved_file_preview_excludes_content(self):
        with tempfile.TemporaryDirectory() as temp:
            # resolve(): macOS temp dirs sit behind the /var symlink, which the policy rejects.
            file = Path(temp).resolve() / "fiction.md"
            file.write_text("violet-marker\nsecond line")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(observe.main(["--file", str(file)]), 0)
            self.assertEqual(json.loads(stdout.getvalue())["candidate_count"], 2)
            self.assertNotIn("violet-marker", stdout.getvalue())
            file.write_text("neurobrain: do-not-store\nviolet-marker")
            with (
                redirect_stdout(io.StringIO()) as stdout,
                redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(observe.main(["--file", str(file)]), 1)
            self.assertFalse(stdout.getvalue())

    def test_notion_scopes_pages_and_checks_whole_snapshot(self):
        page = "00000000-1111-2222-3333-444444444444"

        def response(text, more):
            return dict(
                results=[
                    dict(
                        type="paragraph",
                        has_children=False,
                        paragraph={"rich_text": [{"plain_text": text}]},
                    )
                ],
                has_more=more,
                next_cursor="cursor",
            )

        with (
            patch.object(observe, "setting", return_value="fixture"),
            patch.object(
                observe,
                "request",
                side_effect=[response("violet", True), response("amber", False)],
            ) as http,
        ):
            self.assertEqual(observe.notion_text(page), "violet\namber")
            self.assertTrue(
                all(
                    f"/blocks/{page}/children?" in c.args[0]
                    for c in http.call_args_list
                )
            )
            self.assertIn("start_cursor=cursor", http.call_args.args[0])
        with (
            patch.object(observe, "setting", return_value="fixture"),
            patch.object(
                observe,
                "request",
                side_effect=[
                    response("violet", True),
                    response("neurobrain: do-not-store", False),
                ],
            ),
            self.assertRaises(observe.MemoryError),
        ):
            observe.notion_text(page)
