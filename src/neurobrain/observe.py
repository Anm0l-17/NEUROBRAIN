"""Supervised local preview of one approved page or Markdown file."""

import argparse
import json
import select
import sqlite3
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from uuid import UUID

from .cloud import request, setting
from .core import MemoryError, MemoryStore, NotePolicy, digest, now


def notion_text(page):
    url = f"https://api.notion.com/v1/blocks/{UUID(page)}/children?"
    token = setting("NEUROBRAIN_NOTION_TOKEN")
    params = {"page_size": 100}
    lines = []
    size = 0
    cursors = set()
    while True:
        result = request(
            url + urlencode(params), token, headers={"Notion-Version": "2022-06-28"}
        )
        for block in result["results"]:
            kind = block["type"]
            if block["has_children"] or kind not in {
                "paragraph",
                "heading_1",
                "heading_2",
                "heading_3",
                "to_do",
                "bulleted_list_item",
                "numbered_list_item",
                "quote",
            }:
                raise MemoryError(
                    "Use a flat demo page containing only supported text blocks"
                )
            line = "".join(span["plain_text"] for span in block[kind]["rich_text"])
            size += len(line.encode()) + 1
            if size > NotePolicy.max_bytes:
                raise MemoryError("Page exceeds 1 MiB")
            lines.append(line)
        if not result["has_more"]:
            return NotePolicy.decode("\n".join(lines).encode())
        cursor = result["next_cursor"]
        if not cursor or cursor in cursors or len(cursors) >= 20:
            raise MemoryError("Incomplete page listing")
        cursors.add(cursor)
        params["start_cursor"] = cursor


def load_preview_scorer(path):
    import torch
    from sentence_transformers import SentenceTransformer

    from scripts.train_admission import (
        ENCODER,
        FEATURE_VERSION,
        FROZEN_SHA,
        REVISION,
        AdmissionMLP,
        build_features,
    )

    state = torch.load(path, map_location="cpu", weights_only=True)
    if (state["data_sha256"], state["feature_version"], state["encoder_revision"]) != (
        FROZEN_SHA,
        FEATURE_VERSION,
        REVISION,
    ):
        raise MemoryError("Checkpoint does not match the frozen admission experiment")
    model = AdmissionMLP().eval()
    model.load_state_dict(state["state_dict"])
    encoder = SentenceTransformer(
        ENCODER, revision=REVISION, device="cpu", local_files_only=True
    )

    def score(lines):
        if len(lines) > 128:
            raise MemoryError(
                "Select a short demo document of at most 128 nonblank lines"
            )
        rows = [dict(candidate_text=line, prior_context="") for line in lines]
        features, _, _ = build_features(rows, encoder)
        with torch.inference_mode():
            return model(torch.from_numpy(features)).sigmoid().flatten().tolist()

    return score


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--file", type=Path, help="Exact demo Markdown file edited in VS Code"
    )
    source.add_argument("--notion-page", help="Exact ID of the shared fictional page")
    source.add_argument(
        "--screen-title", help="Exact approved VS Code foreground window title"
    )
    parser.add_argument(
        "--watch", action="store_true", help="Interactive five-minute session"
    )
    parser.add_argument(
        "--checkpoint", type=Path, help="Trusted local MLP for score previews"
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Preview Qwen structured notes from permitted text",
    )
    saving = parser.add_mutually_exclusive_group()
    saving.add_argument(
        "--save-extracted",
        action="store_true",
        help="Save Qwen-selected quotes to the local observation database",
    )
    saving.add_argument(
        "--save-hosted",
        action="store_true",
        help="Explicitly send permitted extracted notes to signed-in Supabase storage",
    )
    parser.add_argument(
        "--db", type=Path, default=Path(".neurobrain/observations.sqlite3")
    )
    parser.add_argument("--notes-root", type=Path, default=Path("examples/notes"))
    args = parser.parse_args(argv)
    try:
        screen = None
        if args.file:
            path = args.file.expanduser().absolute()
            if path.suffix.lower() != ".md" or any(
                p.startswith(".") for p in path.parts
            ):
                raise MemoryError("Select a non-hidden demo Markdown file")
            policy = NotePolicy(path.parent)
            app, route, ref = "VS Code", "selected-file", str(path)

            def read():
                return policy.read(path)[1]
        elif args.notion_page:
            ref = str(UUID(args.notion_page))
            app, route = "Notion", "page-api"

            def read():
                return notion_text(ref)
        else:
            from .screen import ScreenReader

            screen = ScreenReader(args.screen_title)
            app, route, ref = "VS Code", "screen-ocr", args.screen_title
            read = screen.read
            print(
                "Approved window capture: switch to the selected VS Code window within five seconds after start.",
                file=sys.stderr,
            )

        scorer = load_preview_scorer(args.checkpoint) if args.checkpoint else None
        active = not args.watch
        previous = None
        expires = time.monotonic() + 300
        if args.watch:
            if not sys.stdin.isatty():
                raise MemoryError("Watch requires an interactive terminal")
            print(
                f"Stopped | approved {app}: {ref} | local preview | start / pause / resume / stop"
            )
        while time.monotonic() < expires:
            if active:
                text = read()
                fingerprint = digest(text)
                if previous != fingerprint and time.monotonic() < expires:
                    lines = [line for line in text.splitlines() if line.strip()]
                    scores = {"keep_scores": scorer(lines)} if scorer else {}
                    if args.extract or args.save_extracted or args.save_hosted:
                        from .extract import extract_notes

                        scores["extraction"] = extract_notes(text, ref, route)
                    if time.monotonic() >= expires:
                        break
                    if screen:
                        screen.check()
                    if args.save_extracted or args.save_hosted:
                        if args.watch and select.select([sys.stdin], [], [], 0)[0]:
                            # Pending pause/stop takes precedence over persistence.
                            active = False
                            continue
                        if args.save_hosted:
                            from .cloud import save_observation

                            scores["storage"] = save_observation(
                                text, scores["extraction"]
                            )
                        else:
                            with MemoryStore(args.db, args.notes_root) as store:
                                scores["storage"] = store.import_observation(
                                    text, scores["extraction"]
                                )
                    print(
                        json.dumps(
                            dict(
                                app=app,
                                route=route,
                                source=ref,
                                observed_at=now(),
                                event="preview",
                                candidate_count=len(lines),
                                **scores,
                            )
                        ),
                        flush=True,
                    )
                    previous = fingerprint
            if not args.watch:
                break
            if select.select([sys.stdin], [], [], 2)[0]:
                command = sys.stdin.readline().strip().lower()
                if command in {"", "stop"}:
                    break
                if command in {"start", "resume", "pause"}:
                    active = command != "pause"
                    print("Preview active" if active else "Paused", flush=True)
        return 0
    except (
        MemoryError,
        ValueError,
        OSError,
        KeyError,
        TypeError,
        sqlite3.Error,
    ) as exc:
        print(
            str(exc)
            if isinstance(exc, MemoryError)
            else "Invalid source or unavailable input",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
