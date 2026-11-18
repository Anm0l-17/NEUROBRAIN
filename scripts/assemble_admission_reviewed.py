"""Assemble reviewed data with null ambiguity labels; leave release gates open."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from scripts.audit_admission_overlap import connected_groups, load_reviewed
from scripts.score_pilot_reviews import VALUES


def assemble(root):
    rows, hashes = load_reviewed(root)
    for batch in ("01", "02"):
        draft = root / f"data/admission_eval_fresh_{batch}_draft.jsonl"
        reviewed = root / f"data/admission_eval_fresh_{batch}_adjudicated.csv"
        extra = [json.loads(line) for line in draft.read_text().splitlines()]
        with reviewed.open(newline="") as stream:
            submissions = list(csv.DictReader(stream))
        labels = {r["example_id"]: r for r in submissions}
        if len(labels) != len(submissions) or set(labels) != {
            r["example_id"] for r in extra
        }:
            raise ValueError("Fresh draft/review ID mismatch")
        for row in extra:
            label = labels[row["example_id"]]
            for field in ("candidate_text", "prior_context"):
                if label[field] != row[field]:
                    raise ValueError("Fresh draft/review text mismatch")
            for field in VALUES:
                row[field] = label[field]
            row["rationale"] = label["review_rationale"]
            row["review_notes"] = label.get("review_notes", "")
            row["adjudication_note"] = label.get("adjudication_note", "")
        rows.extend(extra)
        for path in (draft, reviewed):
            hashes[str(path.relative_to(root))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    if len({r["example_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate assembled IDs")
    for row in rows:
        for field, allowed in VALUES.items():
            if row[field] not in allowed:
                raise ValueError(f"Invalid {field}: {row['example_id']}")
        if not row["rationale"].strip() or row["split"] != "unassigned":
            raise ValueError(
                "Missing reviewed rationale or unexpectedly assigned split"
            )
        row["label"] = {"keep": 1, "skip": 0, "uncertain": None}[row["action"]]
        row["annotation_status"] = "single_human_reviewed_draft"
        row["label_provenance"] = (
            "solo human review of assistant-authored fictional drafts"
        )
        row["label_state"] = {
            field: "unresolved" if row[field] == "uncertain" else "reviewed"
            for field in ("action", "type", "scope", "sensitivity")
        }
        row.setdefault("parent_id", None)
    rows.sort(key=lambda r: r["example_id"])
    for row, group in zip(rows, connected_groups(rows), strict=True):
        row["origin_component"] = group
    return rows, hashes


def main():
    root = Path(__file__).resolve().parents[1]
    rows, hashes = assemble(root)
    out = root / "data/admission_reviewed_v0_2.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    report = {
        "path": str(out.relative_to(root)),
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "source_sha256": hashes,
        "row_count": len(rows),
        "label_distribution": dict(Counter(r["action"] for r in rows)),
        "origin_components": dict(Counter(r["origin_component"] for r in rows)),
        "head_counts": {
            field: {
                "known": sum(r[field] != "uncertain" for r in rows),
                "unresolved": sum(r[field] == "uncertain" for r in rows),
            }
            for field in ("action", "type", "scope", "sensitivity")
        },
        "status": "reviewed_snapshot_not_training_release",
        "open_gates": [
            "independently assessed validation/test template origins",
            "frozen grouped split manifest",
            "completed Stage B release checklist",
        ],
    }
    (root / "reports/admission_reviewed_v0_2.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        json.dumps({k: v for k, v in report.items() if k != "source_sha256"}, indent=2)
    )


if __name__ == "__main__":
    main()
