"""Single-user, loopback OpenAI-compatible bridge to retained NeuroBrain evidence."""

import argparse
import contextlib
import html
import json
import os
import re
import secrets
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from uuid import uuid4

from .cloud import HostedMemory
from .core import MemoryError, MemoryStore
from .extract import answer

MODEL = "neurobrain-memory"


_PERSONAL = re.compile(r"\b(it|its|they|their|them)\b", re.I)
_DEMONSTRATIVE = re.compile(r"\b(that|this|those)\b", re.I)
_FILLER = frozenset(
    "a an the is are was were be do does did what which who whom whose when where why "
    "how about of to in on at for with and or me my i you tell say said".split()
)


def unresolved_reference(question: str) -> bool:
    """True when the question leans on chat history instead of naming a subject.

    Personal pronouns always count. that/this/those count only when fewer than two
    content words remain, so "the room that Ravi booked" passes but "What about this?" does not.
    shortcut: word list heuristic, not parsing; "How much does that cost?" passes.
    """
    if _PERSONAL.search(question):
        return True
    if not _DEMONSTRATIVE.search(question):
        return False
    words = re.findall(r"[^\W_]+", _DEMONSTRATIVE.sub(" ", question.lower()))
    return sum(w not in _FILLER for w in words) < 2


def literal(text):
    # Source text must not become active links, images or HTML in the chat client.
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~\-])", r"\\\1", html.escape(text))


def create_server(db, notes_root, token, port=8766, answerer=answer, hosted=False):
    if len(token) < 24:
        raise MemoryError("Set NEUROBRAIN_CHAT_KEY to at least 24 characters")

    def open_store():
        return HostedMemory() if hosted else MemoryStore(db, notes_root)

    with open_store():
        pass

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, *_):
            pass

        def send(self, status, value, content_type="application/json"):
            data = (
                value.encode() if isinstance(value, str) else json.dumps(value).encode()
            )
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def authorized(self):
            supplied = self.headers.get("Authorization", "")
            if not secrets.compare_digest(
                supplied.encode(), ("Bearer " + token).encode()
            ):
                self.send(401, {"error": {"message": "Invalid API key"}})
                return False
            return True

        def send_evidence(self, value, content_type, result, question):
            try:
                with open_store() as store, contextlib.ExitStack() as stack:
                    local = getattr(store, "db", None)
                    # Local: serialize final validation and delivery with source deletion.
                    # Hosted: the recheck is the only guard; the server cannot be locked.
                    if local:
                        stack.enter_context(local)
                        local.execute("BEGIN IMMEDIATE")
                    current = {r["citation"]: r["text"] for r in store.search(question)}
                    if any(
                        current.get(r["citation"]) != r["text"]
                        for r in result["answers"]
                    ):
                        self.send(
                            409, {"error": {"message": "Evidence changed; ask again."}}
                        )
                        return
                    self.send(200, value, content_type)
            except (MemoryError, sqlite3.Error, OSError, ValueError):
                self.send(503, {"error": {"message": "Evidence service unavailable"}})

        def do_GET(self):
            if not self.authorized():
                return
            if self.path != "/v1/models":
                self.send(404, {"error": {"message": "Unknown endpoint"}})
                return
            self.send(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": MODEL,
                            "object": "model",
                            "created": 0,
                            "owned_by": "local",
                        }
                    ],
                },
            )

        def do_POST(self):
            if not self.authorized():
                return
            if self.path != "/v1/chat/completions":
                self.send(404, {"error": {"message": "Unknown endpoint"}})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536 or self.headers.get("Transfer-Encoding"):
                    raise ValueError
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or data.get("model") != MODEL:
                    raise ValueError
                messages = data.get("messages")
                if not isinstance(messages, list) or not messages:
                    raise ValueError
                last = messages[-1]
                if not isinstance(last, dict) or last.get("role") != "user":
                    raise ValueError
                question = last.get("content")
                if (
                    not isinstance(question, str)
                    or not question.strip()
                    or len(question) > 2000
                ):
                    raise ValueError
                if type(data.get("stream", False)) is not bool:
                    raise ValueError
                if unresolved_reference(question):
                    self.send(
                        400,
                        {
                            "error": {
                                "message": "Name the subject explicitly in a complete question; this memory endpoint cannot resolve references from chat history."
                            }
                        },
                    )
                    return
            except (ValueError, TypeError, TimeoutError):
                self.send(
                    400,
                    {
                        "error": {
                            "message": "Use a text user question of 1-2000 characters and model neurobrain-memory"
                        }
                    },
                )
                return
            try:
                with open_store() as store:
                    result = answerer(store, question)
                text = (
                    "\n\n".join(
                        f"{literal(r['text'])}\n\n[{r['citation']}] (lines {r['line_start']}-{r['line_end']})"
                        + (
                            f"\nSource: {literal(r['observation']['source'])} ({literal(r['observation']['route'])})"
                            if r.get("observation")
                            else ""
                        )
                        for r in result["answers"]
                    )
                    or "I could not find stored evidence that answers this question."
                )
            except (MemoryError, sqlite3.Error, OSError, ValueError):
                self.send(503, {"error": {"message": "Evidence service unavailable"}})
                return
            common = {
                "id": "chatcmpl-" + uuid4().hex,
                "created": int(time.time()),
                "model": MODEL,
            }
            if data.get("stream"):
                chunks = [
                    {
                        **common,
                        "object": "chat.completion.chunk",
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"role": "assistant", "content": text},
                                "finish_reason": None,
                            }
                        ],
                    },
                    {
                        **common,
                        "object": "chat.completion.chunk",
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                    },
                ]
                body = (
                    "".join("data: " + json.dumps(c) + "\n\n" for c in chunks)
                    + "data: [DONE]\n\n"
                )
                self.send_evidence(body, "text/event-stream", result, question)
            else:
                self.send_evidence(
                    {
                        **common,
                        "object": "chat.completion",
                        "choices": [
                            {
                                "index": 0,
                                "message": {"role": "assistant", "content": text},
                                "finish_reason": "stop",
                            }
                        ],
                    },
                    "application/json",
                    result,
                    question,
                )

    return HTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db", type=Path, default=Path(".neurobrain/observations.sqlite3")
    )
    parser.add_argument("--notes-root", type=Path, default=Path("examples/notes"))
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument(
        "--hosted",
        action="store_true",
        help="Answer from the signed-in Supabase observations (needs NEUROBRAIN_USER_TOKEN)",
    )
    args = parser.parse_args()
    try:
        server = create_server(
            args.db,
            args.notes_root,
            os.environ.get("NEUROBRAIN_CHAT_KEY", ""),
            args.port,
            hosted=args.hosted,
        )
        print(
            f"NeuroBrain evidence endpoint http://127.0.0.1:{server.server_port}/v1",
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    except (MemoryError, OSError, sqlite3.Error):
        parser.exit(
            1, "Cannot start. Check API key length, port, database and notes root.\n"
        )


if __name__ == "__main__":
    main()
