"""Command line adapter over the shared memory services."""

import argparse
import json
import sqlite3
from pathlib import Path

from .core import MemoryError, MemoryStore


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="NeuroBrain local evidence-memory baseline"
    )
    parser.add_argument("--db", type=Path, default=Path(".neurobrain/memory.sqlite3"))
    parser.add_argument(
        "--notes-root",
        type=Path,
        default=Path("examples/notes"),
        help="Only notes inside this explicitly allowed directory can be imported or queried",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    importer = commands.add_parser("import")
    importer.add_argument("path", type=Path)
    commands.add_parser("sources")
    for name in ("search", "ask", "hybrid"):
        sub = commands.add_parser(name)
        sub.add_argument("query")
    inspector = commands.add_parser("inspect")
    inspector.add_argument("source_id")
    forgetter = commands.add_parser("forget")
    forgetter.add_argument("source_id")
    action = forgetter.add_mutually_exclusive_group(required=True)
    action.add_argument("--preview", action="store_true")
    action.add_argument("--confirm", metavar="PREVIEW_TOKEN")
    commands.add_parser("policy")
    server = commands.add_parser("serve")
    server.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    try:
        if args.command == "serve":
            from .web import serve

            serve(args.db, args.notes_root, args.port)
            return 0
        with MemoryStore(args.db, args.notes_root) as store:
            if args.command == "init":
                result = {"status": "ready", "mode": "lexical/extractive", "schema": 1}
            elif args.command == "import":
                result = store.import_note(args.path)
            elif args.command == "sources":
                result = store.sources()
            elif args.command == "search":
                result = store.search(args.query)
            elif args.command == "ask":
                result = store.ask(args.query)
            elif args.command == "hybrid":
                from .semantic import hybrid_search, load_encoder

                encoder, model_error = load_encoder()
                evidence, mode = hybrid_search(store, args.query, encoder)
                result = {
                    "mode": mode,
                    "model_error": model_error,
                    "evidence": evidence,
                }
            elif args.command == "inspect":
                result = store.inspect(args.source_id)
            elif args.command == "forget":
                result = (
                    store.preview_forget(args.source_id)
                    if args.preview
                    else store.forget(args.source_id, args.confirm)
                )
            else:
                result = {
                    "allowed_root": str(store.policy.root),
                    "extensions": [".md", ".txt"],
                    "max_bytes": store.policy.max_bytes,
                    "directive": "neurobrain: do-not-store",
                    "admission": "store all permitted notes; no trained model",
                    "secret_detection": "heuristic only; inspect notes before importing",
                    "training_on_notes": False,
                }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (MemoryError, OSError, sqlite3.Error) as exc:
        message = (
            str(exc)
            if isinstance(exc, MemoryError)
            else "Storage or server unavailable; check paths and permissions."
        )
        print(json.dumps({"error": message}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
