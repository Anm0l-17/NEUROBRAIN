"""Freeze the reviewed snapshot as an explicitly provisional grouped split."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.assemble_admission_reviewed import assemble
from scripts.audit_admission_overlap import connected_groups


def freeze(root: Path):
    rows, source_hashes = assemble(root)
    snapshot = root / "data/admission_reviewed_v0_2.jsonl"
    evidence = json.loads((root / "reports/admission_reviewed_v0_2.json").read_text())
    if (
        source_hashes != evidence["source_sha256"]
        or hashlib.sha256(snapshot.read_bytes()).hexdigest() != evidence["sha256"]
        or rows != [json.loads(line) for line in snapshot.read_text().splitlines()]
    ):
        raise ValueError("Canonical sources differ from the reviewed snapshot")
    groups = connected_groups(rows)
    by_group = defaultdict(list)
    for row, group in zip(rows, groups, strict=True):
        by_group[group].append(row)
    if sorted(map(len, by_group.values())) != [24, 60, 1500]:
        raise ValueError("Unexpected reviewed origin components")
    largest = max(by_group, key=lambda group: len(by_group[group]))
    fresh01 = next(
        group
        for group, members in by_group.items()
        if any(row["example_id"].startswith("eval-fresh-01-") for row in members)
    )
    split_by_group = {largest: "train", fresh01: "validation"}
    split_by_group.update(
        {group: "test" for group in by_group if group not in split_by_group}
    )
    frozen = []
    for row, group in zip(rows, groups, strict=True):
        item = dict(row)
        item["split"] = split_by_group[group]
        frozen.append(item)
    counts = {
        split: {
            "rows": sum(row["split"] == split for row in frozen),
            "keep": sum(
                row["split"] == split and row["action"] == "keep" for row in frozen
            ),
            "skip": sum(
                row["split"] == split and row["action"] == "skip" for row in frozen
            ),
            "uncertain": sum(
                row["split"] == split and row["action"] == "uncertain" for row in frozen
            ),
            "group_ids": sorted(
                {row["origin_component"] for row in frozen if row["split"] == split}
            ),
        }
        for split in ("train", "validation", "test")
    }
    if any(counts[s]["keep"] == 0 or counts[s]["skip"] == 0 for s in counts):
        raise ValueError("Every supervised split needs both known action classes")
    out = root / "data/admission_reviewed_exploratory_v0_1.jsonl"
    payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in frozen)
    manifest = {
        "status": "exploratory_grouped_split_not_independent_release",
        "dataset": str(out.relative_to(root)),
        "dataset_sha256": hashlib.sha256(payload.encode()).hexdigest(),
        "source_sha256": source_hashes,
        "row_count": len(frozen),
        "null_action_labels": sum(row["label"] is None for row in frozen),
        "components": dict(Counter(groups)),
        "splits": counts,
        "split_rule": "largest shared A/B/C component=train; fresh01=validation; fresh02=test",
        "evidence_limits": [
            "A/B/C share one documented assistant template family and stay together.",
            "Fresh01 and fresh02 are provisional authoring families, not proven independent origins.",
            "Fresh02 repeats a fixed five-keep/three-skip/two-uncertain scenario pattern.",
            "Metrics from this file cannot be described as broad held-out generalization.",
        ],
    }
    report = root / "reports/admission_grouped_exploratory_v0_1.json"
    artifacts = [(out, payload), (report, json.dumps(manifest, indent=2) + "\n")]
    for path, contents in artifacts:
        if path.exists() and path.read_bytes() != contents.encode():
            raise ValueError(f"Frozen artifact changed: {path}")
    for path, contents in artifacts:
        if not path.exists():
            with path.open("xb") as stream:
                stream.write(contents.encode("utf-8"))
    return out, report, manifest


def main():
    root = Path(__file__).resolve().parents[1]
    out, report, manifest = freeze(root)
    print(
        json.dumps(
            {"dataset": str(out), "report": str(report), "splits": manifest["splits"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
