import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from neurobrain.chat_api import MODEL, create_server, literal
from neurobrain.core import MemoryStore


class ChatAPITests(unittest.TestCase):
    def test_source_markup_is_literal(self):
        rendered = literal('![image](https://example.com) <img src="remote">')
        self.assertNotIn("![", rendered)
        self.assertNotIn("<img", rendered)
        self.assertIn(r"\!\[image\]\(https://example\.com\)", rendered)

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
