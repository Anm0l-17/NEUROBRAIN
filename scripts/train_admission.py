"""Offline, CPU-only admission pilot. Never connected to application note storage."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from torch import nn

ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
FEATURES = [
    "embedding_0_to_383",
    "capped_log_word_count",
    "heading",
    "list_item",
    "prior_similarity",
]


class AdmissionMLP(nn.Sequential):
    def __init__(self):
        super().__init__(
            nn.Linear(388, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )


def load_rows(path, allow_draft=False):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("Empty dataset")
    seen_ids, seen_text = set(), set()
    groups, families = {}, {}
    for row in rows:
        for key in (
            "example_id",
            "scenario_group",
            "template_family",
            "candidate_text",
            "prior_context",
            "event_time",
            "label",
            "rationale",
            "annotation_status",
            "provenance",
            "split",
        ):
            if key not in row:
                raise ValueError(f"Missing {key}")
        if row["label"] not in (0, 1) or isinstance(row["label"], bool):
            raise ValueError("Labels must be integer 0/1")
        if row["annotation_status"] != "human_reviewed" and not allow_draft:
            raise ValueError(
                "Unreviewed labels: use --allow-draft only for a pipeline trial"
            )
        if row["provenance"].get("kind") != "fictional_assistant_authored":
            raise ValueError("Pilot accepts explicitly fictional fixture data only")
        text = " ".join(row["candidate_text"].lower().split())
        if not text or row["example_id"] in seen_ids or text in seen_text:
            raise ValueError("Empty text, duplicate ID or duplicate candidate")
        seen_ids.add(row["example_id"])
        seen_text.add(text)
        if row["split"] not in ("train", "validation", "test"):
            raise ValueError("Invalid split")
        for lookup, key in ((groups, "scenario_group"), (families, "template_family")):
            previous = lookup.setdefault(row[key], row["split"])
            if previous != row["split"]:
                raise ValueError(f"Cross-split leakage in {key}")
    for split in ("train", "validation", "test"):
        if {r["label"] for r in rows if r["split"] == split} != {0, 1}:
            raise ValueError(f"Both classes required in {split}")
    return rows


def build_features(rows, encoder):
    encoder.eval()
    for parameter in encoder.parameters():
        parameter.requires_grad_(False)
    tokenizer = encoder.tokenizer
    limit = min(256, encoder.max_seq_length)
    texts, truncated = [], 0
    for row in rows:
        candidate = tokenizer.encode(
            "Candidate: " + row["candidate_text"], add_special_tokens=False
        )
        context = tokenizer.encode(
            "Context: " + row["prior_context"], add_special_tokens=False
        )
        budget = limit - tokenizer.num_special_tokens_to_add(pair=False)
        # Candidate gets priority; unused capacity goes to the most recent context.
        kept_candidate = candidate[:budget]
        remaining = budget - len(kept_candidate)
        kept_context = context[-remaining:] if remaining else []
        truncated += int(len(candidate) + len(context) > budget)
        texts.append(
            tokenizer.decode(kept_context + kept_candidate, skip_special_tokens=True)
        )
    with torch.no_grad():
        vectors = encoder.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True
        )
    if vectors.shape != (len(rows), 384) or not np.isfinite(vectors).all():
        raise ValueError("Invalid encoder output")
    extra = np.zeros((len(rows), 4), dtype=np.float32)
    histories = {}
    # No labels, future candidates, or other scenario groups enter the features.
    for i in sorted(
        range(len(rows)), key=lambda j: (rows[j]["event_time"], rows[j]["example_id"])
    ):
        row = rows[i]
        history = histories.setdefault(row["scenario_group"], [])
        text = row["candidate_text"]
        similarity = max((float(vectors[i] @ vectors[j]) for j in history), default=0.0)
        extra[i] = [
            min(math.log1p(len(text.split())) / math.log1p(256), 1.0),
            bool(re.match(r"^\s*#{1,6}\s", text)),
            bool(re.match(r"^\s*(?:[-*+] |\d+[.)] )", text)),
            similarity,
        ]
        history.append(i)
    return np.concatenate([vectors, extra], axis=1).astype(np.float32), texts, truncated


def metrics(labels, scores, threshold):
    predicted = scores >= threshold
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predicted,
        average="binary",
        zero_division=0,
    )
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "average_precision": float(average_precision_score(labels, scores)),
        "confusion_matrix_tn_fp_fn_tp": confusion_matrix(
            labels, predicted, labels=[0, 1]
        )
        .ravel()
        .tolist(),
        "threshold": float(threshold),
        "count": len(labels),
    }


def select_threshold(labels, scores):
    candidates = [float(t) for t in np.unique(np.r_[0.0, scores])]
    eligible = [metrics(labels, scores, t) for t in candidates]
    eligible = [m for m in eligible if m["recall"] >= 0.95]
    return max(eligible, key=lambda m: (m["precision"], m["threshold"]))["threshold"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=Path("data/admission_pilot_v0.jsonl")
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-draft", action="store_true")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.epochs <= 30:
        parser.error("epochs must be in 1..30 for the pilot")
    rows = load_rows(args.data, args.allow_draft)
    args.output.mkdir(parents=True, exist_ok=False)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    encoder = SentenceTransformer(
        ENCODER, revision=REVISION, device="cpu", local_files_only=True
    )
    features, texts, truncated = build_features(rows, encoder)
    labels = np.array([r["label"] for r in rows], dtype=np.float32)
    indices = {
        s: np.array([i for i, r in enumerate(rows) if r["split"] == s])
        for s in ("train", "validation", "test")
    }
    train, valid = indices["train"], indices["validation"]
    x, y = torch.from_numpy(features), torch.from_numpy(labels).view(-1, 1)
    model = AdmissionMLP()
    parameter_count = sum(p.numel() for p in model.parameters())
    assert parameter_count == 53953
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
    criterion = nn.BCEWithLogitsLoss()
    history, best_loss, stale, best = [], float("inf"), 0, None
    for epoch in range(args.epochs):
        model.train()
        order = train[torch.randperm(len(train)).numpy()]
        total = 0.0
        for start in range(0, len(order), 32):
            batch = order[start : start + 32]
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(x[batch]), y[batch])
            if not torch.isfinite(loss):
                raise ValueError("Non-finite training loss")
            loss.backward()
            optimizer.step()
            total += loss.item() * len(batch)
        model.eval()
        with torch.no_grad():
            val_loss = criterion(model(x[valid]), y[valid]).item()
            val_scores = model(x[valid]).sigmoid().flatten().numpy()
        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": total / len(train),
                "validation_loss": val_loss,
                "validation": metrics(labels[valid], val_scores, 0.5),
            }
        )
        if val_loss < best_loss:
            best_loss, stale = val_loss, 0
            best = {
                "state_dict": copy.deepcopy(model.state_dict()),
                "optimizer_state_dict": copy.deepcopy(optimizer.state_dict()),
                "epoch": epoch + 1,
            }
        else:
            stale += 1
        if stale >= 5:
            break
    model.load_state_dict(best["state_dict"])
    model.eval()
    with torch.no_grad():
        scores = model(x).sigmoid().flatten().numpy()
    threshold = select_threshold(labels[valid], scores[valid])
    baselines = {}
    baseline_scores = {
        "store_all": np.ones(len(rows)),
        "majority": np.full(len(rows), float(labels[train].mean() >= 0.5)),
    }
    baseline_scores["rules"] = np.array(
        [
            float(
                bool(
                    re.search(
                        r"\b(prefer|decided|changed|must|always|deadline|unresolved)\b",
                        r["candidate_text"],
                        re.I,
                    )
                )
            )
            for r in rows
        ]
    )
    tfidf = TfidfVectorizer(ngram_range=(1, 2))
    tfidf.fit([texts[i] for i in train])
    for name, values in (
        ("tfidf_logistic", tfidf.transform(texts)),
        ("embedding_logistic", features),
    ):
        logistic = LogisticRegression(max_iter=1000, random_state=args.seed)
        logistic.fit(values[train], labels[train])
        baseline_scores[name] = logistic.predict_proba(values)[:, 1]
    for name, values in baseline_scores.items():
        t = (
            0.5
            if name in ("store_all", "majority", "rules")
            else select_threshold(labels[valid], values[valid])
        )
        baselines[name] = {
            s: metrics(labels[ix], values[ix], t)
            for s, ix in indices.items()
            if s != "train"
        }
    report = {
        "status": "pipeline_trial_only",
        "mode": "suggestion_only_not_integrated",
        "limitations": [
            "Assistant-authored fictional labels; not human-reviewed.",
            "80-example convenience fixture; no generalization or release claims.",
            "No manual near-duplicate audit or downstream QA comparison yet.",
            "One configuration and seed; no seed-variation study or confidence intervals.",
        ],
        "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "encoder": ENCODER,
        "encoder_revision": REVISION,
        "feature_order": FEATURES,
        "truncation": "256 wordpieces maximum; candidate first, then recent context",
        "truncated_examples": truncated,
        "parameters": parameter_count,
        "seed": args.seed,
        "device": "cpu",
        "best_epoch": best["epoch"],
        "splits": {
            s: {
                "rows": len(ix),
                "positive": int(labels[ix].sum()),
                "groups": sorted({rows[i]["scenario_group"] for i in ix}),
            }
            for s, ix in indices.items()
        },
        "metrics": {
            s: metrics(labels[ix], scores[ix], threshold)
            for s, ix in indices.items()
            if s != "train"
        },
        "baselines": baselines,
        "history": history,
        "python": sys.version,
        "dependencies": {
            p: importlib.metadata.version(p)
            for p in ("torch", "numpy", "sentence-transformers", "scikit-learn")
        },
    }
    best.update(
        {
            "threshold": threshold,
            "seed": args.seed,
            "data_sha256": report["data_sha256"],
            "encoder_revision": REVISION,
        }
    )
    torch.save(best, args.output / "checkpoint.pt")
    np.savez(args.output / "reload_fixture.npz", features=features, scores=scores)
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "predictions.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "example_id": r["example_id"],
                    "split": r["split"],
                    "score": float(score),
                    "suggested_keep": bool(score >= threshold),
                }
            )
            + "\n"
            for r, score in zip(rows, scores, strict=True)
        )
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "best_epoch": best["epoch"],
                "status": report["status"],
                "metrics": report["metrics"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
