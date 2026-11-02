"""Compare lexical and offline semantic Recall@5 on fictional paraphrased notes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from neurobrain.core import MemoryStore
from neurobrain.semantic import ENCODER, REVISION, SemanticIndex, load_encoder


def load_cases(path: Path) -> list[dict]:
    cases = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not cases:
        raise ValueError("Semantic evaluation corpus is empty")
    required = {"case_id", "note", "text", "query", "expected_source", "expected_terms"}
    seen_case_ids = set()
    seen_notes = set()
    expected_sources = []
    for case in cases:
        if missing := required - case.keys():
            raise ValueError(f"Missing fields: {sorted(missing)}")
        note = case["note"]
        note_path = Path(note) if isinstance(note, str) else None
        if (
            note_path is None
            or not note_path.parts
            or not note
            or note_path.is_absolute()
            or ".." in note_path.parts
        ):
            raise ValueError(f"Invalid note path: {case['case_id']}")
        if case["case_id"] in seen_case_ids:
            raise ValueError(f"Duplicate case: {case['case_id']}")
        if not isinstance(case["expected_terms"], list) or not case["expected_terms"]:
            raise ValueError(f"Missing expected terms: {case['case_id']}")
        if any(
            not isinstance(term, str) or not term.strip()
            for term in case["expected_terms"]
        ):
            raise ValueError(f"Invalid expected terms: {case['case_id']}")
        normalized_note = note_path.as_posix()
        if normalized_note in seen_notes:
            raise ValueError(f"Duplicate note path: {case['case_id']}")
        seen_case_ids.add(case["case_id"])
        seen_notes.add(normalized_note)
        expected_source = case["expected_source"]
        if not isinstance(expected_source, str):
            raise ValueError(f"Invalid expected source: {case['case_id']}")
        expected_path = Path(expected_source)
        if expected_path.is_absolute() or ".." in expected_path.parts:
            raise ValueError(f"Invalid expected source: {case['case_id']}")
        expected_sources.append((case["case_id"], expected_path.as_posix()))
    for case_id, expected_source in expected_sources:
        if expected_source not in seen_notes:
            raise ValueError(f"Unknown expected source: {case_id}")
    return cases


def run(cases: list[dict]) -> dict:
    encoder, encoder_error = load_encoder()
    with tempfile.TemporaryDirectory(prefix="neurobrain-semantic-") as directory:
        base = Path(directory).resolve()
        notes = base / "notes"
        notes.mkdir()
        with MemoryStore(base / "memory.sqlite3", notes) as store:
            for case in cases:
                path = notes / case["note"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(case["text"].encode("utf-8"))
                store.import_note(path)
            semantic = None
            if encoder is not None:
                semantic = SemanticIndex(store, encoder)
                semantic.rebuild()
            results = []
            for case in cases:
                lexical = store.search(case["query"])
                semantic_hits = semantic.search(case["query"]) if semantic else []
                expected_path = (notes / case["expected_source"]).resolve()
                lexical_passed = any(
                    Path(hit["path"]) == expected_path
                    and all(term in hit["text"] for term in case["expected_terms"])
                    for hit in lexical
                )
                semantic_passed = (
                    any(
                        Path(hit["path"]) == expected_path
                        and all(term in hit["text"] for term in case["expected_terms"])
                        for hit in semantic_hits
                    )
                    if semantic
                    else None
                )
                results.append(
                    {
                        "case_id": case["case_id"],
                        "lexical": lexical_passed,
                        "semantic": semantic_passed,
                    }
                )
            return {
                "name": "neurobrain-semantic-v0",
                "encoder": ENCODER,
                "revision": REVISION,
                "semantic_available": semantic is not None,
                "fallback": "lexical" if semantic is None else None,
                "model_error": encoder_error,
                "cases": len(cases),
                "lexical_recall_at_5": sum(r["lexical"] for r in results)
                / len(results),
                "semantic_recall_at_5": sum(r["semantic"] for r in results)
                / len(results)
                if semantic
                else None,
                "fallback_recall_at_5": sum(r["lexical"] for r in results)
                / len(results)
                if semantic is None
                else None,
                "results": results,
            }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=Path("data/semantic_evaluation_v0.jsonl")
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(load_cases(args.data))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
