import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from neurobrain.chat_api import MODEL, create_server, literal, unresolved_reference
from neurobrain.core import MemoryStore


class ChatAPITests(unittest.TestCase):
    def test_source_markup_is_literal(self):
        rendered = literal('![image](https://example.com) <img src="remote">')
        self.assertNotIn("![", rendered)
        self.assertNotIn("<img", rendered)
        self.assertIn(r"\!\[image\]\(https://example\.com\)", rendered)

    def test_reference_guard_refuses_only_history_dependent_questions(self):
        for ok in (
            "What is the room number that Ravi booked?",
            "Which budget review is this quarter?",
            "Is the amber rehearsal room that Mira booked free?",
        ):
            self.assertFalse(unresolved_reference(ok), ok)
        for bad in (
            "What about it?",
            "When is its deadline?",
            "What did they decide?",
            "What about this?",
            "Which room is that?",
        ):
            self.assertTrue(unresolved_reference(bad), bad)

    def test_hosted_bridge_answers_from_supabase_and_never_serves_forgotten_rows(self):
        from neurobrain.core import MemoryError as NBError

        row = dict(
            citation="s:0",
            text="The violet demonstration is on 23 November 2026.",
            path="Notion",
            line_start=1,
            line_end=1,
            observation=dict(source="Notion", route="page-api"),
        )

        def answerer(store, question):
            return {"answers": store.search(question)}

        key = "test-only-" * 4
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            with patch.dict(os.environ, {"NEUROBRAIN_USER_TOKEN": "user"}):
                server = create_server(
                    root / "unused.sqlite3", root, key, 0, answerer, hosted=True
                )
                thread = threading.Thread(target=server.serve_forever)
                thread.start()
                try:

                    def ask():
                        body = dict(
                            model=MODEL,
                            messages=[
                                dict(
                                    role="user",
                                    content="When is the violet demonstration?",
                                )
                            ],
                        )
                        req = Request(
                            f"http://127.0.0.1:{server.server_port}/v1/chat/completions",
                            json.dumps(body).encode(),
                            {
                                "Authorization": "Bearer " + key,
                                "Content-Type": "application/json",
                            },
                        )
                        with urlopen(req, timeout=5) as response:
                            return response.read().decode()

                    with patch("neurobrain.cloud.rpc", return_value=[row]) as rpc:
                        self.assertIn("s:0", ask())
                        self.assertEqual(
                            rpc.call_args.args[0]["folder"], "observations"
                        )
                    with patch("neurobrain.cloud.rpc", return_value=[]):
                        self.assertNotIn("s:0", ask())
                    with patch("neurobrain.cloud.rpc", side_effect=NBError("down")):
                        with self.assertRaises(HTTPError) as error:
                            ask()
                        self.assertEqual(error.exception.code, 503)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(NBError):
                    create_server(
                        root / "u.sqlite3", root, key, 0, answerer, hosted=True
                    )

    def test_auth_discovery_streaming_and_forgetting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            db = root / "memory.sqlite3"
            note = root / "demo.md"
            note.write_text("The demo is on Friday.")
            with MemoryStore(db, root) as store:
                source = store.import_note(note)["source_id"]
            key = "test-only-" * 4
            revoke_before_delivery = False

            def answerer(store, question):
                rows = store.search(question)
                if revoke_before_delivery and rows:
                    target = rows[0]["source_id"]
                    preview = store.preview_forget(target)
                    store.forget(target, preview["preview_token"])
                return {"answers": rows}

            server = create_server(db, root, key, 0, answerer)
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}/v1"

                def call(path, body=None, token=key):
                    req = Request(
                        base + path,
                        json.dumps(body).encode() if body else None,
                        {
                            "Authorization": "Bearer " + token,
                            "Content-Type": "application/json",
                        },
                    )
                    with urlopen(req, timeout=5) as response:
                        return response.read().decode()

                with self.assertRaises(HTTPError) as error:
                    call("/models", token="wrong")
                self.assertEqual(error.exception.code, 401)
                self.assertEqual(json.loads(call("/models"))["data"][0]["id"], MODEL)
                body = dict(model=MODEL, messages=[dict(role="user", content="Friday")])
                self.assertIn(source, call("/chat/completions", body))
                stream = call("/chat/completions", dict(body, stream=True))
                self.assertIn("data: [DONE]", stream)
                self.assertIn(source, stream)
                with MemoryStore(db, root) as store:
                    preview = store.preview_forget(source)
                    store.forget(source, preview["preview_token"])
                self.assertNotIn(source, call("/chat/completions", body))
                with self.assertRaises(HTTPError) as error:
                    call("/chat/completions", dict(body, messages=[]))
                self.assertEqual(error.exception.code, 400)
                with self.assertRaises(HTTPError) as error:
                    call(
                        "/chat/completions",
                        dict(
                            body,
                            messages=[
                                dict(role="user", content="When is its deadline?")
                            ],
                        ),
                    )
                self.assertEqual(error.exception.code, 400)
                self.assertIn("Name the subject", error.exception.read().decode())
                note.write_text("The changed Friday demonstration has a fresh marker.")
                with MemoryStore(db, root) as store:
                    store.import_note(note)
                revoke_before_delivery = True
                with self.assertRaises(HTTPError) as error:
                    call("/chat/completions", body)
                self.assertEqual(error.exception.code, 409)
                self.assertNotIn("fresh marker", error.exception.read().decode())
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
