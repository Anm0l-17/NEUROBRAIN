"""Optional offline semantic retrieval experiment over the SQLite baseline."""

from __future__ import annotations

import threading
from dataclasses import dataclass

from .core import MemoryError, MemoryStore

ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
_ENCODER = None
_ENCODER_ERROR = None
_ENCODER_ATTEMPTED = False
_INDEX_CACHE = {}
_INDEX_LOCK = threading.Lock()


def invalidate_cache(store: MemoryStore) -> None:
    """Drop cached indexes for a database after source deletion."""

    db_path = store.db.execute("PRAGMA database_list").fetchone()[2]
    for key in list(_INDEX_CACHE):
        if key[0] == db_path:
            _INDEX_CACHE.pop(key, None)


def load_encoder():
    """Load the pinned local encoder, or return an explicit fallback error."""

    global _ENCODER, _ENCODER_ERROR, _ENCODER_ATTEMPTED
    if _ENCODER_ATTEMPTED:
        return _ENCODER, _ENCODER_ERROR
    _ENCODER_ATTEMPTED = True
    try:
        from sentence_transformers import SentenceTransformer

        _ENCODER = SentenceTransformer(
            ENCODER, revision=REVISION, device="cpu", local_files_only=True
        )
    except (ImportError, OSError, RuntimeError) as exc:
        _ENCODER_ERROR = f"{type(exc).__name__}: {exc}"
    return _ENCODER, _ENCODER_ERROR


@dataclass(frozen=True)
class SemanticHit:
    """A lexical-compatible evidence result with a cosine similarity score."""

    source_id: str
    id: int
    path: str
    version: int
    text: str
    char_start: int
    char_end: int
    line_start: int
    line_end: int
    score: float
    citation: str

    def as_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "id": self.id,
            "path": self.path,
            "version": self.version,
            "text": self.text,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "score": self.score,
            "citation": self.citation,
        }


class SemanticIndex:
    """Rebuildable in-memory embeddings over active, policy-allowed chunks."""

    def __init__(self, store: MemoryStore, encoder):
        self.store = store
        self.encoder = encoder
        self._rows: list[dict] = []
        self._vectors = None
        self._state_token = None

    def _current_state(self) -> tuple:
        return tuple(
            tuple(row)
            for row in self.store.db.execute(
                "SELECT id,path,content_hash,active FROM sources ORDER BY id"
            )
        )

    def rebuild(self) -> None:
        import numpy as np

        rows = self.store.db.execute(
            """SELECT c.*,s.path,s.version
            FROM chunks c JOIN sources s ON s.id=c.source_id
            WHERE s.active=1 ORDER BY c.id"""
        ).fetchall()
        allowed = [dict(row) for row in rows if self.store._allowed(row["path"])]
        if not allowed:
            self._rows = []
            self._vectors = np.empty((0, 0), dtype=np.float32)
            self._state_token = self._current_state()
            return
        vectors = self.encoder.encode(
            [row["text"] for row in allowed],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[0] != len(allowed):
            raise MemoryError("The embedding model returned an invalid shape.")
        if not np.isfinite(vectors).all() or not np.allclose(
            np.linalg.norm(vectors, axis=1), 1.0, atol=1e-3
        ):
            raise MemoryError("The embedding model returned invalid vectors.")
        self._rows = allowed
        self._vectors = vectors
        self._state_token = self._current_state()

    def rebuild_if_stale(self) -> None:
        if self._state_token != self._current_state():
            self.rebuild()

    def search(self, query: str, limit: int = 5) -> list[dict]:
        import numpy as np

        if not query.strip() or not 1 <= limit <= 20:
            raise MemoryError("Use a non-empty query and a limit from 1 to 20.")
        if not self._rows or self._vectors is None:
            return []
        active_ids = {
            row["id"]
            for row in self.store.db.execute("SELECT id FROM sources WHERE active=1")
        }
        allowed_rows = [
            i
            for i, row in enumerate(self._rows)
            if row["source_id"] in active_ids and self.store._allowed(row["path"])
        ]
        if not allowed_rows:
            return []
        vector = np.asarray(
            self.encoder.encode(
                [query], normalize_embeddings=True, convert_to_numpy=True
            ),
            dtype=np.float32,
        )
        if vector.shape != (1, self._vectors.shape[1]) or not np.isfinite(vector).all():
            raise MemoryError("The embedding model returned an invalid query vector.")
        scores = self._vectors @ vector[0]
        order = sorted(allowed_rows, key=lambda i: (-scores[i], i))[:limit]
        return [
            SemanticHit(
                source_id=self._rows[i]["source_id"],
                id=self._rows[i]["id"],
                path=self._rows[i]["path"],
                version=self._rows[i]["version"],
                text=self._rows[i]["text"],
                char_start=self._rows[i]["char_start"],
                char_end=self._rows[i]["char_end"],
                line_start=self._rows[i]["line_start"],
                line_end=self._rows[i]["line_end"],
                score=float(scores[i]),
                citation=f"{self._rows[i]['source_id']}:{self._rows[i]['id']}",
            ).as_dict()
            for i in order
        ]


def hybrid_search(
    store: MemoryStore, query: str, encoder, limit: int = 5
) -> tuple[list[dict], str]:
    """Fuse lexical and semantic evidence with reciprocal rank fusion."""

    lexical = store.search(query, limit=limit)
    if encoder is None:
        return lexical, "lexical-fallback"
    db_path = store.db.execute("PRAGMA database_list").fetchone()[2]
    cache_key = (db_path, str(store.policy.root))
    with _INDEX_LOCK:
        index = _INDEX_CACHE.get(cache_key)
        if index is None or index.encoder is not encoder:
            index = SemanticIndex(store, encoder)
            _INDEX_CACHE[cache_key] = index
        else:
            index.store = store
        index.rebuild_if_stale()
        semantic = index.search(query, limit=limit)
    fused = {}
    for rank, hit in enumerate(lexical, start=1):
        fused.setdefault(hit["citation"], {**hit, "fused_score": 0.0})
        fused[hit["citation"]]["fused_score"] += 1 / (60 + rank)
    for rank, hit in enumerate(semantic, start=1):
        fused.setdefault(hit["citation"], {**hit, "fused_score": 0.0})
        fused[hit["citation"]]["fused_score"] += 1 / (60 + rank)
    results = sorted(
        fused.values(), key=lambda hit: (-hit["fused_score"], hit["citation"])
    )
    return results[:limit], "hybrid-rrf"
