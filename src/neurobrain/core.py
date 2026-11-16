"""Shared deterministic services. No models, telemetry, or network calls."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


class MemoryError(ValueError):
    """A controlled user-facing input or policy error."""


def now() -> str:
    return datetime.now(UTC).isoformat()


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class NotePolicy:
    """Explicit directory allowlist and conservative input restrictions.

    Secret checks are a demo guardrail, not a complete secret detector.
    """

    max_bytes = 1_048_576
    blocked_parts = frozenset({".git", ".ssh", ".aws", ".codex", ".env", "secrets"})

    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        if not self.root.is_dir():
            raise MemoryError("The allowed notes directory does not exist.")

    def read(self, path: Path) -> tuple[Path, str]:
        selected = path.expanduser().absolute()
        if any(p.is_symlink() for p in (selected, *selected.parents)):
            raise MemoryError("Symbolic links are not allowed for note imports.")
        resolved = selected.resolve()
        if not resolved.is_relative_to(self.root):
            raise MemoryError("This file is outside the allowed notes directory.")
        relative = resolved.relative_to(self.root)
        if any(
            p.lower() in self.blocked_parts or p.startswith(".") for p in relative.parts
        ):
            raise MemoryError("Hidden or excluded paths cannot be imported.")
        if resolved.suffix.lower() not in {".md", ".txt"}:
            raise MemoryError("Only Markdown and TXT files are supported.")
        try:
            # Bounded read even when the file grows during import.
            with resolved.open("rb") as stream:
                raw = stream.read(self.max_bytes + 1)
        except OSError as exc:
            raise MemoryError("The selected note cannot be read.") from exc
        return resolved, self.decode(raw)

    @classmethod
    def decode(cls, raw: bytes) -> str:
        if len(raw) > cls.max_bytes:
            raise MemoryError("Notes must be at most 1 MiB.")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MemoryError("The selected note must be UTF-8 text.") from exc
        if not text.strip() or "\x00" in text:
            raise MemoryError("Empty or binary notes cannot be imported.")
        if re.search(r"(?im)^\s*(?:<!--\s*)?neurobrain:\s*do[- ]not[- ]store\b", text):
            raise MemoryError("The note contains a NeuroBrain do-not-store directive.")
        if re.search(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
            r"|\b(?:password|api[_ -]?key|access[_ -]?token)\s*[:=]\s*\S+",
            text,
            re.IGNORECASE,
        ):
            raise MemoryError(
                "The note contains a possible credential; import refused."
            )
        return text


SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
INSERT OR IGNORE INTO schema_version VALUES(1);
CREATE TABLE IF NOT EXISTS sources(
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    version INTEGER NOT NULL,
    imported_at TEXT NOT NULL,
    active INTEGER NOT NULL CHECK(active IN (0,1)),
    UNIQUE(path, version)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_source ON sources(path) WHERE active=1;
CREATE TABLE IF NOT EXISTS chunks(
    id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    UNIQUE(source_id, ordinal)
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, content='chunks', content_rowid='id');
CREATE TRIGGER IF NOT EXISTS chunk_insert AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid,text) VALUES(new.id,new.text);
END;
CREATE TRIGGER IF NOT EXISTS chunk_delete AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts,rowid,text) VALUES('delete',old.id,old.text);
END;
CREATE TABLE IF NOT EXISTS tombstones(content_hash TEXT PRIMARY KEY, deleted_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS deletion_receipts(
    id TEXT PRIMARY KEY,
    completed_at TEXT NOT NULL,
    source_count INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS observation_metadata(
    source_id TEXT PRIMARY KEY REFERENCES sources(id) ON DELETE CASCADE,
    metadata TEXT NOT NULL
);
"""


def norm(text):
    """Whitespace-insensitive form, so OCR text and the saved file compare equal."""
    return " ".join(text.split())


def passages(text):
    offset = 0
    while offset < len(text):
        end = min(offset + 1200, len(text))
        if end < len(text):
            boundary = text.rfind("\n", offset + 600, end)
            if boundary >= 0:
                end = boundary + 1
        if text[offset:end].strip():
            yield (
                text[offset:end],
                offset,
                end,
                text.count("\n", 0, offset) + 1,
                text.count("\n", 0, end - 1) + 1,
            )
        offset = end


class MemoryStore:
    """Application memory with transactional FTS deletion and versioned evidence."""

    def __init__(self, db: Path, notes_root: Path):
        self.policy = NotePolicy(notes_root)
        db = db.expanduser().resolve()
        db.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA secure_delete=ON")
        self.db.execute("PRAGMA journal_mode=DELETE")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.db.close()
            raise MemoryError(
                "Unsupported database version; use the matching application."
            )
        self.db.executescript("BEGIN;\n" + SCHEMA + "\nPRAGMA user_version=1;\nCOMMIT;")

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def import_note(self, path: Path) -> dict:
        path, text = self.policy.read(path)
        return self._import(path, text, list(passages(text)))

    def import_observation(self, text: str, extraction: dict) -> dict:
        from .extract import extract_notes

        # Validate evidence again at persistence, even for caller-supplied extraction.
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
        if checked["source_sha256"] != extraction["source_sha256"]:
            raise MemoryError("Observation changed after extraction")
        if checked["notes"] != extraction["notes"]:
            raise MemoryError("Observation evidence offsets differ")
        checked["status"] = "saved_by_explicit_extraction_request"
        key = [extraction["route"], extraction["source"]]
        if extraction["route"] == "screen-ocr":
            # Each distinct capture is its own source, so scrolling never hides earlier notes.
            key.append(digest(text))
        path = self.policy.root / ("observation-" + digest(json.dumps(key)) + ".md")
        rows = [
            (n["text"], n["char_start"], n["char_end"], n["line_start"], n["line_end"])
            for n in checked["notes"]
        ]
        return self._import(path, text, rows, checked)

    def _import(self, path, text, rows, metadata=None):
        content_hash = digest(text)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self.db.execute(
                "SELECT 1 FROM tombstones WHERE content_hash=?", (content_hash,)
            ).fetchone():
                raise MemoryError(
                    "This exact content was forgotten and is blocked from re-import."
                )
            previous = self.db.execute(
                "SELECT * FROM sources WHERE path=? ORDER BY version DESC LIMIT 1",
                (str(path),),
            ).fetchone()
            same_observation = True
            if previous and metadata is not None:
                stored = self.db.execute(
                    "SELECT metadata FROM observation_metadata WHERE source_id=?",
                    (previous["id"],),
                ).fetchone()
                old = json.loads(stored["metadata"]) if stored else {}
                # Observation time changes on retries; evidence and policy identity matter.
                same_observation = {
                    k: v for k, v in metadata.items() if k != "observed_at"
                } == {k: v for k, v in old.items() if k != "observed_at"}
            if (
                previous
                and previous["content_hash"] == content_hash
                and same_observation
            ):
                return {
                    "source_id": previous["id"],
                    "version": previous["version"],
                    "duplicate": True,
                }
            version = previous["version"] + 1 if previous else 1
            self.db.execute("UPDATE sources SET active=0 WHERE path=?", (str(path),))
            source_id = uuid4().hex
            self.db.execute(
                "INSERT INTO sources VALUES(?,?,?,?,?,1)",
                (source_id, str(path), content_hash, version, now()),
            )
            ordinal = 0
            for passage in rows:
                self.db.execute(
                    """INSERT INTO chunks(source_id,ordinal,text,char_start,char_end,line_start,line_end)
                    VALUES(?,?,?,?,?,?,?)""",
                    (source_id, ordinal, *passage),
                )
                ordinal += 1
            if metadata is not None:
                self.db.execute(
                    "INSERT INTO observation_metadata VALUES(?,?)",
                    (source_id, json.dumps(metadata)),
                )
        return {
            "source_id": source_id,
            "version": version,
            "chunks": ordinal,
            "duplicate": False,
        }

    def _allowed(self, path: str) -> bool:
        """Reapply path scope at query time without rereading the original note."""
        candidate = Path(path)
        if not candidate.is_relative_to(self.policy.root):
            return False
        relative = candidate.relative_to(self.policy.root)
        return not any(
            p.lower() in self.policy.blocked_parts or p.startswith(".")
            for p in relative.parts
        )

    def sources(self) -> list[dict]:
        rows = self.db.execute(
            """SELECT s.*,count(c.id) AS chunks,m.metadata FROM sources s
            LEFT JOIN chunks c ON c.source_id=s.id
            LEFT JOIN observation_metadata m ON m.source_id=s.id
            GROUP BY s.id ORDER BY s.imported_at DESC"""
        ).fetchall()
        sources = []
        logical = {}
        for row in rows:
            if not self._allowed(row["path"]):
                continue
            key = self._logical_key(row["id"]) if row["active"] else None
            if key and key in logical:
                logical[key]["linked"].append(row["id"])
                continue
            source = dict(row)
            metadata = source.pop("metadata")
            if metadata is not None:
                observation = json.loads(metadata)
                source["observation"] = {
                    key: observation[key] for key in ("source", "route")
                }
            source["linked"] = []
            if key:
                logical[key] = source
            sources.append(source)
        return sources

    def _logical_key(self, source_id):
        texts = frozenset(
            norm(r[0])
            for r in self.db.execute(
                "SELECT text FROM chunks WHERE source_id=?", (source_id,)
            )
        )
        return texts or None

    def inspect(self, source_id: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM sources WHERE id=?", (source_id,)
        ).fetchone()
        if not row or not self._allowed(row["path"]):
            raise MemoryError("Source not found in the allowed notes scope.")
        metadata = self.db.execute(
            "SELECT metadata FROM observation_metadata WHERE source_id=?", (source_id,)
        ).fetchone()
        return {
            "observation": json.loads(metadata[0]) if metadata else None,
            "source": dict(row),
            "chunks": [
                dict(r)
                for r in self.db.execute(
                    "SELECT * FROM chunks WHERE source_id=? ORDER BY ordinal",
                    (source_id,),
                )
            ],
        }

    def observation_reference(self, source_id: str):
        row = self.db.execute(
            "SELECT metadata FROM observation_metadata WHERE source_id=?", (source_id,)
        ).fetchone()
        if row is None:
            return None
        metadata = json.loads(row["metadata"])
        return {key: metadata[key] for key in ("source", "route")}

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if not 1 <= limit <= 20 or len(query) > 2000:
            raise MemoryError(
                "Use a query up to 2,000 characters and a limit from 1 to 20."
            )
        tokens = re.findall(r"[^\W_]+", query, re.UNICODE)[:32]
        if not tokens:
            return []
        # Treat input as literal terms, never as caller-supplied FTS syntax.
        expression = " OR ".join('"' + t + '"' for t in tokens)
        rows = self.db.execute(
            """SELECT c.*,s.path,s.version,s.imported_at,bm25(chunks_fts) AS rank
            FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.rowid
            JOIN sources s ON s.id=c.source_id
            WHERE chunks_fts MATCH ? AND s.active=1
            ORDER BY rank,c.id""",
            (expression,),
        )
        results = []
        seen = {}
        for row in rows:
            if self._allowed(row["path"]):
                first = seen.get(norm(row["text"]))
                if first is not None:
                    # Same note reached through another route: link, don't repeat.
                    first["linked"].append(f"{row['source_id']}:{row['id']}")
                    continue
                item = dict(row)
                item["citation"] = f"{item['source_id']}:{item['id']}"
                item["observation"] = self.observation_reference(item["source_id"])
                item["linked"] = []
                seen[norm(item["text"])] = item
                results.append(item)
                if len(results) == limit:
                    break
        return results

    def ask(self, question: str) -> dict:
        evidence = self.search(question)
        return {
            "mode": "extractive",
            "status": "matching_passages" if evidence else "no_evidence",
            "message": (
                "Matching note excerpts follow; relevance does not establish an answer. No language model is connected."
                if evidence
                else "No matching evidence found. I cannot answer from the stored notes."
            ),
            "evidence": evidence,
        }

    def preview_forget(self, source_id: str) -> dict:
        inspected = self.inspect(source_id)
        source = inspected["source"]
        observation = inspected["observation"] or {}
        window = (
            [observation["source"]] if observation.get("route") == "screen-ocr" else []
        )
        # Plain and extracted imports of one note share content but not path:
        # also take in-scope copies whose exact content matches any version.
        rows = [
            row
            for row in self.db.execute(
                """SELECT s.id,s.path,s.content_hash,count(c.id) AS chunks FROM sources s
                LEFT JOIN chunks c ON c.source_id=s.id
                WHERE s.path=? OR s.content_hash IN
                    (SELECT content_hash FROM sources WHERE path=?)
                    OR s.id IN (SELECT source_id FROM observation_metadata
                        WHERE json_extract(metadata,'$.route')='screen-ocr'
                        AND json_extract(metadata,'$.source') IN (SELECT value FROM json_each(?)))
                GROUP BY s.id ORDER BY s.path,s.version""",
                (source["path"], source["path"], json.dumps(window)),
            )
            if self._allowed(row["path"])
        ]
        # Same note via another route differs in bytes (trailing newline, OCR spacing):
        # also take in-scope sources holding a chunk with the same normalized text.
        # shortcut: scans every chunk, fine at demo size; add a normalized-hash column to scale.
        wanted = {
            norm(c[0])
            for row in rows
            for c in self.db.execute(
                "SELECT text FROM chunks WHERE source_id=?", (row["id"],)
            )
        }
        have = {row["id"] for row in rows}
        for row in self.db.execute(
            """SELECT s.id,s.path,s.content_hash,count(c.id) AS chunks FROM sources s
            LEFT JOIN chunks c ON c.source_id=s.id GROUP BY s.id ORDER BY s.path,s.version"""
        ):
            if row["id"] in have or not self._allowed(row["path"]):
                continue
            if wanted & {
                norm(c[0])
                for c in self.db.execute(
                    "SELECT text FROM chunks WHERE source_id=?", (row["id"],)
                )
            }:
                rows.append(row)
        content_hashes = sorted({row["content_hash"] for row in rows})
        source_ids = [row["id"] for row in rows]
        chunks = sum(row["chunks"] for row in rows)
        token = digest("|".join(source_ids + content_hashes + [str(chunks)]))
        return {
            "source_ids": source_ids,
            "versions": len(rows),
            "chunks": chunks,
            "preview_token": token,
            "scope": "All imported versions of this source, copies with identical content, other captures of the same screen window, and their FTS entries",
            "boundary": "Original files, backups, and previously displayed answers remain outside this deletion.",
        }

    def forget(self, source_id: str, preview_token: str) -> dict:
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            preview = self.preview_forget(source_id)
            if preview_token != preview["preview_token"]:
                raise MemoryError(
                    "Deletion preview is stale; preview the source again."
                )
            completed = now()
            for sid in preview["source_ids"]:
                row = self.db.execute(
                    "SELECT content_hash FROM sources WHERE id=?", (sid,)
                ).fetchone()
                self.db.execute(
                    "INSERT OR IGNORE INTO tombstones VALUES(?,?)", (row[0], completed)
                )
                self.db.execute("DELETE FROM sources WHERE id=?", (sid,))
            receipt_id = uuid4().hex
            self.db.execute(
                "INSERT INTO deletion_receipts VALUES(?,?,?,?)",
                (receipt_id, completed, preview["versions"], preview["chunks"]),
            )
            # The FTS integrity command verifies external-content index consistency.
            self.db.execute(
                "INSERT INTO chunks_fts(chunks_fts,rank) VALUES('integrity-check',1)"
            )
            if self.db.execute("PRAGMA foreign_key_check").fetchall():
                raise MemoryError(
                    "Deletion integrity check failed; transaction rolled back."
                )
        try:
            from .semantic import invalidate_cache

            invalidate_cache(self)
        except ImportError:
            pass
        return {
            "receipt_id": receipt_id,
            "completed_at": completed,
            "removed_versions": preview["versions"],
            "removed_chunks": preview["chunks"],
            "verified": True,
            "original_file_deleted": False,
        }
