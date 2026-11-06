"""Compare two completed, independent admission-pilot review CSVs."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

VALUES = {
    "action": {"keep", "skip", "uncertain"},
    "type": {
        "decision",
        "preference",
        "requirement",
        "milestone",
        "correction",
        "unresolved_issue",
        "fact",
        "transient",
        "acknowledgment",
        "uncertain",
    },
    "scope": {"person", "project", "session", "uncertain"},
    "sensitivity": {"ordinary", "personal", "restricted", "uncertain"},
    "source": {"fictional_assistant_authored", "uncertain"},
}


def load_review(path, expected_ids):
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if (
        len(rows) != len(expected_ids)
        or {r.get("example_id") for r in rows} != expected_ids
    ):
        raise ValueError(f"{path}: expected exactly the 80 pilot IDs")
    if len({r["example_id"] for r in rows}) != len(rows):
        raise ValueError(f"{path}: duplicate example ID")
    for row in rows:
        for field, allowed in VALUES.items():
            if row.get(field) not in allowed:
                raise ValueError(
                    f"{path}: invalid or missing {field} for {row['example_id']}"
                )
    return {r["example_id"]: r for r in rows}


def binary_kappa(pairs):
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    first, second = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum(first[label] * second[label] for label in ("keep", "skip")) / n**2
    return None if expected == 1 else (observed - expected) / (1 - expected)


def compare(first, second):
    ids = sorted(first)
    pairs = [(first[i]["action"], second[i]["action"]) for i in ids]
    binary = [(a, b) for a, b in pairs if a != "uncertain" and b != "uncertain"]
    type_ids = [
        i
        for i in ids
        if first[i]["type"] != "uncertain" and second[i]["type"] != "uncertain"
    ]
    scope_ids = [
        i
        for i in ids
        if first[i]["scope"] != "uncertain" and second[i]["scope"] != "uncertain"
    ]
    return {
        "rows": len(ids),
        "keep_skip_rows": len(binary),
        "excluded_from_kappa_as_uncertain": len(ids) - len(binary),
        "keep_skip_agreement": sum(a == b for a, b in binary) / len(binary)
        if binary
        else None,
        "keep_skip_cohens_kappa": binary_kappa(binary),
        "type_rows": len(type_ids),
        "type_agreement": sum(first[i]["type"] == second[i]["type"] for i in type_ids)
        / len(type_ids)
        if type_ids
        else None,
        "scope_rows": len(scope_ids),
        "scope_agreement": sum(
            first[i]["scope"] == second[i]["scope"] for i in scope_ids
        )
        / len(scope_ids)
        if scope_ids
        else None,
        "disagreements": [
            {
                "example_id": i,
                "fields": [
                    field for field in VALUES if first[i][field] != second[i][field]
                ],
            }
            for i in ids
            if any(first[i][field] != second[i][field] for field in VALUES)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviewer_one", type=Path)
    parser.add_argument("reviewer_two", type=Path)
    args = parser.parse_args()
    if args.reviewer_one.resolve() == args.reviewer_two.resolve():
        parser.error("provide two separate review files")
    template = (
        Path(__file__).resolve().parents[1] / "data/admission_pilot_v0_blind_review.csv"
    )
    with template.open(encoding="utf-8", newline="") as stream:
        expected_ids = {r["example_id"] for r in csv.DictReader(stream)}
    if len(expected_ids) != 80:
        raise ValueError("Blind review template must contain 80 unique IDs")
    first = load_review(args.reviewer_one, expected_ids)
    second = load_review(args.reviewer_two, expected_ids)
    print(json.dumps(compare(first, second), indent=2))


if __name__ == "__main__":
    main()
