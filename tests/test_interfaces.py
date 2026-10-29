import contextlib
import http.client
import io
import json
import re
import tempfile
import threading
import unittest
from pathlib import Path

from neurobrain.cli import main
from neurobrain.web import create_server


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.base = Path(self.directory.name).resolve()
        self.root = self.base / "notes"
        self.root.mkdir()
        (self.root / "demo.md").write_text(
            "WebCanary uses SQLite.\n<script>alert('x')</script>"
        )
        self.db = self.base / "memory.sqlite3"

    def tearDown(self):
        self.directory.cleanup()

    def cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["--db", str(self.db), "--notes-root", str(self.root), *args])
        return code, json.loads(output.getvalue())

    def test_cli_lifecycle_and_controlled_error(self):
        self.assertEqual(self.cli("init")[0], 0)
        _, imported = self.cli("import", str(self.root / "demo.md"))
        self.assertEqual(
            self.cli("search", "SQLite")[1][0]["source_id"], imported["source_id"]
        )
        _, preview = self.cli("forget", imported["source_id"], "--preview")
        self.assertEqual(
            self.cli(
                "forget", imported["source_id"], "--confirm", preview["preview_token"]
            )[0],
            0,
        )
        self.assertEqual(self.cli("search", "WebCanary")[1], [])
        self.assertEqual(self.cli("import", str(self.root / "demo.md"))[0], 1)

    def test_http_cli_parity_and_browser_request_protection(self):
        server = create_server(self.db, self.root, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def request(method, path, payload=None, token=None, **extra):
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_port, timeout=5
            )
            headers = {"Content-Type": "application/json", **extra}
            if token:
                headers["X-NeuroBrain-Token"] = token
            connection.request(
                method,
                path,
                body=json.dumps(payload) if payload is not None else None,
                headers=headers,
            )
            response = connection.getresponse()
            result = (
                response.status,
                response.read().decode(),
                dict(response.getheaders()),
            )
            connection.close()
            return result

        try:
            code, page, headers = request("GET", "/")
            self.assertEqual(code, 200)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertIn("textContent", page)
            self.assertNotIn("innerHTML", page)
            token = re.search(r"const token='([^']+)'", page).group(1)
            self.assertEqual(request("GET", "/api/sources")[0], 403)
            self.assertEqual(
                request("POST", "/api/import", {"path": "demo.md"})[0], 403
            )
            self.assertEqual(request("GET", "/", Host="attacker.example")[0], 403)
            self.assertEqual(
                request(
                    "POST",
                    "/api/import",
                    {"path": "demo.md"},
                    token,
                    Origin="https://attacker.example",
                )[0],
                403,
            )
            self.assertEqual(
                request("POST", "/api/import", {"path": "../outside.md"}, token)[0], 400
            )
            code, body, _ = request("POST", "/api/import", {"path": "demo.md"}, token)
            self.assertEqual(code, 200)
            sid = json.loads(body)["source_id"]
            code, body, _ = request("GET", "/api/search?q=SQLite", token=token)
            self.assertEqual(code, 200)
            self.assertEqual(
                json.loads(body)["evidence"], self.cli("search", "SQLite")[1]
            )
            preview = json.loads(
                request("GET", "/api/preview?id=" + sid, token=token)[1]
            )
            result = request(
                "POST",
                "/api/forget",
                {"id": sid, "preview_token": preview["preview_token"]},
                token,
            )
            self.assertEqual(result[0], 200)
            self.assertEqual(self.cli("search", "WebCanary")[1], [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
