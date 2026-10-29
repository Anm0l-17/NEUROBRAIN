"""Loopback-only demonstration UI, using the same services as the CLI.

The standard-library server is for a single-user local demo, not deployment.
"""

import json
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .core import MemoryError, MemoryStore


def create_server(db: Path, notes_root: Path, port: int = 8765) -> HTTPServer:
    token = secrets.token_urlsafe(32)
    page = (
        Path(__file__)
        .with_name("index.html")
        .read_text(encoding="utf-8")
        .replace("__TOKEN__", token)
    )
    # Fail before binding if the store cannot initialize.
    with MemoryStore(db, notes_root):
        pass

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *_):
            # Avoid logging questions, filenames, or private text.
            pass

        def send(self, status, data, html=False):
            body = (
                data.encode("utf-8")
                if html
                else json.dumps(data, ensure_ascii=False).encode("utf-8")
            )
            self.send_response(status)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
                if html
                else "application/json; charset=utf-8",
            )
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'nonce-"
                + token
                + "'; style-src 'nonce-"
                + token
                + "'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            allowed = {
                f"127.0.0.1:{self.server.server_port}",
                f"localhost:{self.server.server_port}",
            }
            if self.headers.get("Host") not in allowed:
                self.send(
                    403, {"error": "Only the local application address is allowed."}
                )
                return False
            origin = self.headers.get("Origin")
            if origin and origin not in {"http://" + host for host in allowed}:
                self.send(403, {"error": "Cross-origin requests are blocked."})
                return False
            return True

        def do_GET(self):
            if not self.authorized():
                return
            url = urlsplit(self.path)
            if url.path == "/":
                self.send(200, page, html=True)
                return
            if self.headers.get("X-NeuroBrain-Token") != token:
                self.send(403, {"error": "Open the local app to access memory."})
                return
            query = parse_qs(url.query)
            try:
                with MemoryStore(db, notes_root) as store:
                    if url.path == "/api/sources":
                        result = store.sources()
                    elif url.path == "/api/search":
                        result = store.ask(query.get("q", [""])[0])
                    elif url.path == "/api/inspect":
                        result = store.inspect(query.get("id", [""])[0])
                    elif url.path == "/api/preview":
                        result = store.preview_forget(query.get("id", [""])[0])
                    else:
                        self.send(404, {"error": "Unknown route."})
                        return
                self.send(200, result)
            except MemoryError as exc:
                self.send(400, {"error": str(exc)})
            except (OSError, sqlite3.Error):
                self.send(503, {"error": "Local storage is unavailable."})

        def do_POST(self):
            if not self.authorized():
                return
            if self.headers.get("X-NeuroBrain-Token") != token:
                self.send(403, {"error": "Missing application token."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 16384:
                    raise MemoryError("Request size is invalid.")
                if self.headers.get("Content-Type") != "application/json":
                    raise MemoryError("Use a JSON request.")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict) or not all(
                    isinstance(v, str) for v in payload.values()
                ):
                    raise MemoryError("Request fields must be text.")
                with MemoryStore(db, notes_root) as store:
                    if self.path == "/api/import":
                        relative = Path(payload.get("path", ""))
                        if relative.is_absolute():
                            raise MemoryError(
                                "Select a path relative to the allowed notes directory."
                            )
                        result = store.import_note(store.policy.root / relative)
                    elif self.path == "/api/forget":
                        result = store.forget(
                            payload.get("id", ""), payload.get("preview_token", "")
                        )
                    else:
                        self.send(404, {"error": "Unknown route."})
                        return
                self.send(200, result)
            except (ValueError, UnicodeError) as exc:
                message = (
                    str(exc)
                    if isinstance(exc, MemoryError)
                    else "Invalid JSON request."
                )
                self.send(400, {"error": message})
            except (OSError, sqlite3.Error):
                self.send(503, {"error": "Local storage is unavailable."})

    server = HTTPServer(("127.0.0.1", port), Handler)
    server.timeout = 1
    return server


def serve(db: Path, notes_root: Path, port: int = 8765):
    server = create_server(db, notes_root, port)
    print(
        f"NeuroBrain: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
