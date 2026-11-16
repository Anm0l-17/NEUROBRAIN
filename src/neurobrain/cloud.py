"""Stage C2 CLI for a selected Drive folder and a signed-in Supabase user."""

import argparse
import getpass
import json
import os
import re
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .core import MemoryError, NotePolicy, digest, passages


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def request(url, token, *, payload=None, key=None, raw=False, headers=None):
    headers = dict(headers or {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if key:
        headers["apikey"] = key
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = Request(
        url, json.dumps(payload).encode() if payload is not None else None, headers
    )
    try:
        with build_opener(NoRedirect()).open(req, timeout=20) as response:
            result = response.read(NotePolicy.max_bytes + 1)
    except HTTPError as exc:
        detail = ""
        if exc.code == 400:
            body = exc.read(4096)
            for message in (
                "Content previously forgotten",
                "Invalid operation or stale confirmation",
                "Unknown source",
            ):
                if message.encode() in body:
                    detail = ": " + message
        raise MemoryError(f"Cloud request failed (HTTP {exc.code}){detail}") from exc
    except (URLError, OSError) as exc:
        raise MemoryError("Cloud service unreachable") from exc
    if len(result) > NotePolicy.max_bytes:
        raise MemoryError("Cloud response exceeds 1 MiB")
    return result if raw else json.loads(result)


def setting(name):
    value = os.environ.get(name)
    if not value:
        raise MemoryError(f"Set {name} locally")
    return value


def identifier(value):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", value):
        raise MemoryError("Expected a Drive ID")
    return value


def allowed(meta, folder):
    name = meta.get("name", "")
    return (
        folder in meta.get("parents", [])
        and not meta.get("trashed", True)
        and "/" not in name
        and "\\" not in name
        and not name.startswith(".")
        and PurePosixPath(name).suffix.lower() in {".txt", ".md"}
        and not meta.get("mimeType", "").startswith("application/vnd.google-apps.")
        and int(meta.get("size", NotePolicy.max_bytes + 1)) <= NotePolicy.max_bytes
    )


def drive(op, folder, file_id):
    token = setting("NEUROBRAIN_DRIVE_TOKEN")
    base = "https://www.googleapis.com/drive/v3/files"
    fields = "id,name,parents,trashed,mimeType,size,version"
    if op == "list":
        params = {
            "q": f"'{folder}' in parents and trashed = false",
            "pageSize": 100,
            "fields": f"nextPageToken,files({fields})",
        }
        files = []
        while True:
            page = request(base + "?" + urlencode(params), token)
            files.extend(
                {"id": m["id"], "name": m["name"]}
                for m in page["files"]
                if allowed(m, folder)
            )
            if not page.get("nextPageToken"):
                return files
            params["pageToken"] = page["nextPageToken"]
    url = base + "/" + identifier(file_id)
    meta_url = url + "?" + urlencode({"fields": fields})
    meta = request(meta_url, token)
    if not allowed(meta, folder):
        raise MemoryError("File outside selected folder or excluded by note policy")
    text = NotePolicy.decode(request(url + "?alt=media", token, raw=True))
    if meta != request(meta_url, token):
        raise MemoryError("Drive file changed during import. Retry.")
    return {
        "filename": meta["name"],
        "revision": meta["version"],
        "body_hash": digest(text),
        "pieces": list(passages(text)),
    }


def rpc(params):
    base = setting("SUPABASE_URL").rstrip("/")
    if not re.fullmatch(r"https://[a-z0-9-]+\.supabase\.co", base):
        raise MemoryError("Expected a hosted Supabase project URL")
    key = setting("SUPABASE_PUBLISHABLE_KEY")
    token = os.environ.get("NEUROBRAIN_USER_TOKEN")
    if not token:
        email = setting("NEUROBRAIN_DEMO_EMAIL")
        token = request(
            base + "/auth/v1/token?grant_type=password",
            None,
            key=key,
            payload={
                "email": email,
                "password": getpass.getpass("Demo account password: "),
            },
        )["access_token"]
    return request(base + "/rest/v1/rpc/c2_memory", token, key=key, payload=params)


def save_observation(text, extraction):
    from .extract import extract_notes

    checked = extract_notes(
        text,
        extraction["source"],
        extraction["route"],
        lambda _: {
            "notes": [
                {"kind": n["kind"], "quote": n["text"]} for n in extraction["notes"]
            ]
        },
    )
    if (
        checked["source_sha256"] != extraction["source_sha256"]
        or checked["notes"] != extraction["notes"]
    ):
        raise MemoryError("Observation evidence changed before hosted save")
    if checked["route"] not in {"selected-file", "page-api", "screen-ocr"}:
        raise MemoryError("Unsupported hosted observation route")
    checked["status"] = "saved_by_explicit_hosted_request"
    key = [checked["route"], checked["source"]]
    if checked["route"] == "screen-ocr":
        # Same keying as MemoryStore: each distinct capture is its own hosted source.
        key.append(digest(text))
    source_key = "obs_" + digest(json.dumps(key))
    params = dict(
        op="import",
        folder="observations",
        file_id=source_key,
        filename=checked["source"],
        body_hash=checked["source_sha256"],
        observation=checked,
        pieces=[
            [n["text"], n["char_start"], n["char_end"], n["line_start"], n["line_end"]]
            for n in checked["notes"]
        ],
    )
    result = rpc(params)
    if (
        not isinstance(result, dict)
        or not result.get("source_id")
        or type(result.get("version")) is not int
    ):
        raise MemoryError("Hosted write did not return an acknowledgment")
    return {**result, "storage": "supabase", "source_key": source_key}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m neurobrain.cloud")
    cmds = parser.add_subparsers(dest="op", required=True)
    cmds.add_parser("list")
    for name in ("import", "inspect", "preview", "forget"):
        sub = cmds.add_parser(name)
        sub.add_argument("file_id")
        if name == "forget":
            sub.add_argument("--confirm", required=True)
    cmds.add_parser("search").add_argument("query")
    args = parser.parse_args(argv)
    try:
        folder = identifier(setting("NEUROBRAIN_DRIVE_FOLDER"))
        if args.op == "list":
            result = drive("list", folder, None)
        else:
            params = {"op": args.op, "folder": folder}
            if hasattr(args, "file_id"):
                params["file_id"] = identifier(args.file_id)
            if args.op == "import":
                params.update(drive("import", folder, args.file_id))
            elif args.op == "search":
                params["query_text"] = args.query
            elif args.op == "forget":
                params["confirmation"] = args.confirm
            result = rpc(params)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (MemoryError, ValueError, KeyError, EOFError) as exc:
        print(
            str(exc)
            if isinstance(exc, MemoryError)
            else "Unexpected cloud response or missing input"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
