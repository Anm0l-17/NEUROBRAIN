"""Offline overlap screen for reviewed A/B/C data; does not assign splits."""

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from neurobrain.semantic import ENCODER, REVISION, load_encoder


def load_reviewed(root):
    drafts = [root / f"data/admission_batch_a_draft_{i:02d}.jsonl" for i in range(1, 6)]
    drafts += [root / f"data/admission_batch_{b}_draft.jsonl" for b in ("b", "c")]
    labels = [root / f"data/admission_batch_a_adjudicated_{i:02d}.csv" for i in (1, 2)]
    labels += [root / "data/admission_batch_a_review_03_completed.csv"]
    labels += [root / f"data/admission_batch_a_adjudicated_{i:02d}.csv" for i in (4, 5)]
    labels += [
        root / "data/admission_batch_b_adjudicated_v1_1.csv",
        root / "data/admission_batch_c_review_completed.csv",
    ]
    rows = [
        json.loads(line)
        for p in drafts
        for line in p.read_text().splitlines()
        if line.strip()
    ]
    reviewed = []
    for p in labels:
        with p.open(newline="") as stream:
            reviewed.extend(csv.DictReader(stream))
    by_id = {r["example_id"]: r for r in reviewed}
    if len(by_id) != len(reviewed) or len({r["example_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate source or review IDs")
    if set(by_id) != {r["example_id"] for r in rows}:
        raise ValueError("Draft/review ID mismatch")
    for row in rows:
        review = by_id[row["example_id"]]
        for field in ("candidate_text", "prior_context"):
            if field in review and review[field] != row[field]:
                raise ValueError(f"Reviewed text differs: {row['example_id']}")
        for field in ("action", "type", "scope", "sensitivity", "source"):
            row[field] = review[field]
        row["rationale"] = review["review_rationale"]
        row["review_notes"] = review.get("review_notes", "")
        row["adjudication_note"] = review.get("adjudication_note", "")
        row["label"] = {"keep": 1, "skip": 0, "uncertain": None}[row["action"]]
    hashes = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in drafts + labels
    }
    return sorted(rows, key=lambda r: r["example_id"]), hashes


def connected_groups(rows):
    """Shared scenarios or template roots connect records transitively."""
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen = {}
    for i, row in enumerate(rows):
        for field in ("scenario_group", "template_family"):
            value = row[field]
            if not value:
                raise ValueError(f"Missing {field}")
            key = (field, value)
            if key in seen:
                parent[find(i)] = find(seen[key])
            else:
                seen[key] = i
    ids = {r.get("example_id"): i for i, r in enumerate(rows)}
    origins = {}
    for i, row in enumerate(rows):
        if row.get("parent_id"):
            if row["parent_id"] not in ids:
                raise ValueError("Unknown clarification parent")
            parent[find(i)] = find(ids[row["parent_id"]])
        if row.get("paraphrase_origin"):
            origin = origins.setdefault(row["paraphrase_origin"], i)
            parent[find(i)] = find(origin)
            if row["paraphrase_origin"] in ids:
                parent[find(i)] = find(ids[row["paraphrase_origin"]])
    roots = sorted({find(i) for i in range(len(rows))})
    names = {root: f"origin-component-{n:03d}" for n, root in enumerate(roots)}
    return [names[find(i)] for i in range(len(rows))]


def main():
    import numpy as np

    root = Path(__file__).resolve().parents[1]
    rows, hashes = load_reviewed(root)
    assert len(rows) == 1500
    assert Counter(r["action"] for r in rows) == {
        "keep": 918,
        "skip": 504,
        "uncertain": 78,
    }
    assert all(r["label"] is None for r in rows if r["action"] == "uncertain")
    assert all(r["split"] == "unassigned" for r in rows)
    groups = connected_groups(rows)
    encoder, error = load_encoder()
    if encoder is None:
        raise RuntimeError(f"Offline semantic encoder unavailable: {error}")
    candidates = [r["candidate_text"] for r in rows]
    # Context is screened separately; repeated long contexts can dominate similarity.
    contexts = [r["prior_context"] for r in rows]
    vectors = encoder.encode(
        candidates, normalize_embeddings=True, convert_to_numpy=True
    )
    context_vectors = encoder.encode(
        contexts, normalize_embeddings=True, convert_to_numpy=True
    )
    assert vectors.shape == context_vectors.shape == (1500, 384)
    assert np.isfinite(vectors).all() and np.isfinite(context_vectors).all()
    scores = vectors @ vectors.T
    context_scores = context_vectors @ context_vectors.T

    def norm(s):
        return re.sub(r"\W+", " ", s.casefold()).strip()

    exact = Counter(norm(t) for t in candidates)
    pairs = []
    for i, a in enumerate(rows):
        for j in range(i + 1, len(rows)):
            b = rows[j]
            if a["scenario_group"] == b["scenario_group"]:
                continue
            candidate_score, context_score = (
                float(scores[i, j]),
                float(context_scores[i, j]),
            )
            if candidate_score < 0.85 and context_score < 0.90:
                continue
            pairs.append(
                {
                    "id_a": a["example_id"],
                    "id_b": b["example_id"],
                    "candidate_cosine": round(candidate_score, 6),
                    "context_cosine": round(context_score, 6),
                    "candidate_flag": candidate_score >= 0.85,
                    "context_flag": context_score >= 0.90,
                    "cross_batch": a["example_id"][6] != b["example_id"][6],
                    "action_a": a["action"],
                    "action_b": b["action"],
                    "text_a": a["candidate_text"],
                    "text_b": b["candidate_text"],
                }
            )
    pairs.sort(key=lambda p: (-p["candidate_cosine"], p["id_a"], p["id_b"]))
    out = root / "reports/admission_overlap"
    out.mkdir(exist_ok=True)
    fields = [
        "id_a",
        "id_b",
        "candidate_cosine",
        "context_cosine",
        "candidate_flag",
        "context_flag",
        "cross_batch",
        "action_a",
        "action_b",
        "text_a",
        "text_b",
    ]
    with (out / "flagged_pairs.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(pairs)
    assignments = [
        {
            "example_id": r["example_id"],
            "scenario_group": r["scenario_group"],
            "template_family": r["template_family"],
            "origin_component": group,
            "split": "unassigned",
            "action": r["action"],
            "label": r["label"],
        }
        for r, group in zip(rows, groups, strict=True)
    ]
    (out / "grouping.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in assignments)
    )
    summary = {
        "encoder": ENCODER,
        "revision": REVISION,
        "source_sha256": hashes,
        "rows": len(rows),
        "scenarios": len({r["scenario_group"] for r in rows}),
        "origin_components": dict(Counter(groups)),
        "actions": dict(Counter(r["action"] for r in rows)),
        "normalized_exact_candidate_duplicate_excess": sum(
            n - 1 for n in exact.values()
        ),
        "candidate_cosine_threshold": 0.85,
        "context_cosine_threshold": 0.90,
        "flagged_pairs": len(pairs),
        "candidate_flag_pairs": sum(p["candidate_flag"] for p in pairs),
        "cross_batch_candidate_flag_pairs": sum(
            p["candidate_flag"] and p["cross_batch"] for p in pairs
        ),
        "context_flag_pairs": sum(p["context_flag"] for p in pairs),
        "decision": "Keep the shared origin component together; fresh validation/test origins required.",
        "limits": [
            "Cosine thresholds screen for inspection; they are not calibrated duplicate decisions.",
            "Low similarity does not establish independent origin.",
            "Encoder truncation applies; long contexts may lose detail.",
            "Candidate rows are independent snapshots; no conversation history is inferred.",
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps({k: v for k, v in summary.items() if k != "source_sha256"}, indent=2)
    )


if __name__ == "__main__":
    main()
