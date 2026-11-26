import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
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

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_off_unless_the_flag_is_one(self):
        for value in ("", "0"):
            self.hybrid(value, encoder=FakeEncoder())
            with MemoryStore(self.db, self.root) as store:
                self.assertEqual(search_evidence(store, "Which venue?"), [])

    def test_lexical_without_the_encoder(self):
        self.hybrid()
        with MemoryStore(self.db, self.root) as store:
            self.assertEqual(search_evidence(store, "Which venue?"), [])
            self.assertEqual(len(search_evidence(store, "cafe")), 1)

    def test_hosted_memory_keeps_its_own_search(self):
        self.hybrid(encoder=object())
        hosted = Mock(spec=["search"])
        self.assertIs(search_evidence(hosted, "cafe"), hosted.search.return_value)

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_save_during_an_index_rebuild_is_not_missed(self):
        test = self

        class SavesWhileEncoding(FakeEncoder):
            saved = False

            def encode(self, texts, **kwargs):
                if not self.saved:
                    self.saved = True
                    test.save("hall.md", "Another cafe is in Hall C.")
                return super().encode(texts, **kwargs)

        self.hybrid(encoder=SavesWhileEncoding())
        with MemoryStore(self.db, self.root) as store:
            search_evidence(store, "Which venue?")
            self.assertEqual(len(search_evidence(store, "Which venue?")), 2)

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_index_picks_up_saves_from_another_connection(self):
        self.hybrid(encoder=FakeEncoder())
        with MemoryStore(self.db, self.root) as store:
            self.assertEqual(len(search_evidence(store, "Which venue?")), 1)
            self.save("hall.md", "Another cafe is in Hall C.")
            self.assertEqual(len(search_evidence(store, "Which venue?")), 2)

    @unittest.skipIf(np is None, "numpy unavailable")
    def test_linked_copy_takes_one_slot(self):
        self.save("copy.md", "The cafe closed for repairs.\n")
        self.hybrid(encoder=FakeEncoder())
        with MemoryStore(self.db, self.root) as store:
            self.assertEqual(len(search_evidence(store, "cafe")), 1)


if __name__ == "__main__":
    unittest.main()
