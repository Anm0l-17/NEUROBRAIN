import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen

from neurobrain import semantic
from neurobrain.chat_api import create_server
from neurobrain.core import MemoryStore
from neurobrain.extract import answer, search_evidence

try:
    import numpy as np
except ImportError:
    np = None


class FakeEncoder:
    """Puts "venue" next to "cafe", which share no word."""

    def encode(self, texts, **_):
        return np.array(
            [[1.0, 0.0] if "venue" in t or "cafe" in t else [0.0, 1.0] for t in texts],
            dtype=np.float32,
        )


class HybridAnswerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.db = self.root / "memory.sqlite3"
        self.save("cafe.md", "The cafe closed for repairs.")
        self.addCleanup(semantic._INDEX_CACHE.clear)

    def save(self, name, text):
        note = self.root / name
        note.write_text(text)
        with MemoryStore(self.db, self.root) as store:
            store.import_note(note)

    def hybrid(self, value="1", encoder=None):
        env = patch.dict(os.environ, {"NEUROBRAIN_HYBRID": value})
        load = patch.object(
            semantic, "load_encoder", return_value=(encoder, "missing")
        )
        env.start()
        load.start()
        self.addCleanup(env.stop)
        self.addCleanup(load.stop)

    @staticmethod
    def cite_all(payload):
        return {
            "citations": payload["format"]["properties"]["citations"]["items"]["enum"]
        }

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_note_found_only_by_the_encoder_survives_both_rechecks(self):
        self.hybrid(encoder=FakeEncoder())
        server = create_server(
            self.db,
            self.root,
            "k" * 24,
            port=0,
            answerer=lambda store, q: answer(store, q, self.cite_all),
        )
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        body = {
            "model": "neurobrain-memory",
            "messages": [{"role": "user", "content": "Which venue?"}],
        }
        request = Request(
            f"http://127.0.0.1:{server.server_port}/v1/chat/completions",
            json.dumps(body).encode(),
            {"Authorization": "Bearer " + "k" * 24},
        )
        with urlopen(request, timeout=10) as response:
            text = json.load(response)["choices"][0]["message"]["content"]
        self.assertIn("closed for repairs", text)

    def test_off_by_default_and_lexical_without_the_encoder(self):
        for value, query, expected in (
            ("", "Which venue?", 0),
            ("1", "Which venue?", 0),
            ("1", "cafe", 1),
        ):
            self.hybrid(value)
            with MemoryStore(self.db, self.root) as store:
                self.assertEqual(len(search_evidence(store, query)), expected)

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_index_picks_up_saves_from_another_connection(self):
        self.hybrid(encoder=FakeEncoder())
        with MemoryStore(self.db, self.root) as store:
            self.assertEqual(len(search_evidence(store, "Which venue?")), 1)
            self.save("hall.md", "The new venue is Hall C.")
            self.assertEqual(len(search_evidence(store, "Which venue?")), 2)

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_linked_copy_takes_one_slot(self):
        self.save("copy.md", "The cafe closed for repairs.\n")
        self.hybrid(encoder=FakeEncoder())
        with MemoryStore(self.db, self.root) as store:
            self.assertEqual(len(search_evidence(store, "cafe")), 1)


if __name__ == "__main__":
    unittest.main()
