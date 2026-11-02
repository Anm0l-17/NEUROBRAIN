"""Run the deterministic NeuroBrain v0 baseline against fictional evaluation cases."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from neurobrain.core import MemoryStore


def load_cases(path: Path) -> list[dict]:
    cases = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    required = {"case_id", "kind", "note", "text", "query", "expected_terms"}
    if not cases:
        raise ValueError("Evaluation corpus is empty")
    seen = set()
    seen_notes = set()
    for case in cases:
        missing = required - case.keys()
        if missing:
            raise ValueError(f"Missing fields in evaluation case: {sorted(missing)}")
        if case["case_id"] in seen:
            raise ValueError(f"Duplicate evaluation case: {case['case_id']}")
        if case["kind"] not in {"answerable", "unsupported", "deletion", "retained"}:
            raise ValueError(f"Invalid evaluation case kind: {case['kind']}")
        for field in ("note", "expected_source"):
            value = case.get(field, "")
            if not isinstance(value, str):
                raise ValueError(f"{field} must be text: {case['case_id']}")
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Invalid {field} path: {case['case_id']}")
        if case["kind"] != "unsupported" and not case["note"]:
            raise ValueError(f"Missing note: {case['case_id']}")
        if case["note"]:
            normalized_note = Path(case["note"]).as_posix()
            if normalized_note in seen_notes:
                raise ValueError(f"Duplicate note path: {case['case_id']}")
            seen_notes.add(normalized_note)
        if case["kind"] != "unsupported" and not case.get("expected_source"):
            raise ValueError(f"Missing expected_source: {case['case_id']}")
        if not isinstance(case["expected_terms"], list):
            raise ValueError(f"expected_terms must be a list: {case['case_id']}")
        if case["kind"] != "unsupported" and (
            not case["expected_terms"]
            or any(
                not isinstance(term, str) or not term.strip()
                for term in case["expected_terms"]
            )
        ):
            raise ValueError(f"Expected terms must be nonempty text: {case['case_id']}")
        seen.add(case["case_id"])
    return cases


def run(cases: list[dict]) -> dict:
    answerable = [
        case for case in cases if case["kind"] in {"answerable", "deletion", "retained"}
    ]
    unsupported = [case for case in cases if case["kind"] == "unsupported"]
    deletion_cases = [case for case in cases if case["kind"] == "deletion"]
    retained_cases = [case for case in cases if case["kind"] == "retained"]
    if not deletion_cases or not retained_cases:
        raise ValueError("Evaluation corpus needs deletion and retained cases")
    with tempfile.TemporaryDirectory(prefix="neurobrain-baseline-") as directory:
        base = Path(directory).resolve()
        notes = base / "notes"
        notes.mkdir()
        db = base / "memory.sqlite3"
        with MemoryStore(db, notes) as store:
            source_ids = {}
            note_texts = {}
            for case in cases:
                if case["note"]:
                    path = notes / case["note"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(case["text"].encode("utf-8"))
                    source_ids[case["note"]] = store.import_note(path)["source_id"]
                    note_texts[str(path)] = case["text"]

            answerable_results = []
            for case in answerable:
                hits = store.search(case["query"])
                matching = [
                    hit
                    for hit in hits
                    if all(term in hit["text"] for term in case["expected_terms"])
                ]

                def citation_is_valid(hit: dict) -> bool:
                    source_text = note_texts.get(hit["path"])
                    return bool(
                        source_text is not None
                        and hit["citation"] == f"{hit['source_id']}:{hit['id']}"
                        and source_text[hit["char_start"] : hit["char_end"]]
                        == hit["text"]
                    )

                citation_valid = bool(matching) and all(
                    citation_is_valid(hit) for hit in matching
                )
                expected_path = (notes / case["expected_source"]).resolve()
                source_match = any(
                    Path(hit["path"]) == expected_path for hit in matching
                )
                answerable_results.append(
                    {
                        "case_id": case["case_id"],
                        "passed": bool(matching and source_match and citation_valid),
                        "hits": len(hits),
                        "citation_valid": citation_valid,
                    }
                )

            unsupported_results = []
            for case in unsupported:
                unsupported_results.append(
                    {
                        "case_id": case["case_id"],
                        "passed": not store.search(case["query"]),
                    }
                )

            retained_checks = [
                (source_ids[case["note"]], case) for case in retained_cases
            ]
            deletion_results = []
            for deletion in deletion_cases:
                deletion_source_id = source_ids[deletion["note"]]
                deletion_hits_before = any(
                    hit["source_id"] == deletion_source_id
                    for hit in store.search(deletion["query"])
                )
                retained_before = all(
                    any(
                        hit["source_id"] == retained_source_id
                        for hit in store.search(case["query"])
                    )
                    for retained_source_id, case in retained_checks
                )
                preview = store.preview_forget(deletion_source_id)
                receipt = store.forget(deletion_source_id, preview["preview_token"])
                deletion_hits_after = any(
                    hit["source_id"] == deletion_source_id
                    for hit in store.search(deletion["query"])
                )
                retained_after = all(
                    any(
                        hit["source_id"] == retained_source_id
                        for hit in store.search(case["query"])
                    )
                    for retained_source_id, case in retained_checks
                )
                deletion_results.append(
                    {
                        "case_id": deletion["case_id"],
                        "passed": bool(
                            deletion_hits_before
                            and receipt["verified"]
                            and not deletion_hits_after
                            and retained_before
                            and retained_after
                        ),
                        "receipt_verified": receipt["verified"],
                        "deleted_hits_after": deletion_hits_after,
                        "retained_hits_after": retained_after,
                    }
                )

        passed_answerable = sum(result["passed"] for result in answerable_results)
        passed_unsupported = sum(result["passed"] for result in unsupported_results)
        return {
            "name": "neurobrain-lexical-extractive-v0",
            "cases": len(cases),
            "answerable_recall": passed_answerable / len(answerable),
            "unsupported_abstention": passed_unsupported / len(unsupported)
            if unsupported
            else 1.0,
            "citation_validity": sum(
                result["citation_valid"] for result in answerable_results
            )
            / len(answerable),
            "deletions": deletion_results,
            "answerable": answerable_results,
            "unsupported": unsupported_results,
            "passed": all(
                result["passed"] for result in answerable_results + unsupported_results
            )
            and all(result["passed"] for result in deletion_results),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/evaluation_v0.jsonl"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = run(load_cases(args.data))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
