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
from collections import Counter, defaultdict
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
FEATURE_VERSION = "snapshot-v1"
HEAD_LABELS = {
    "action": {"keep", "skip"},
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
    },
    "scope": {"person", "project", "session"},
    "sensitivity": {"ordinary", "personal", "restricted"},
}


class AdmissionMLP(nn.Sequential):
    def __init__(self, dropout=0.2):
        super().__init__(
            nn.Linear(388, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )


FROZEN_SHA = "d91b7314d7e751351f0e6f6e58cd64dfafa4913e7e1be3381ec87599b192dab1"


def action_value(row):
    label = row.get("label")
    if "label" not in row or (
        label is not None and (type(label) is not int or label not in (0, 1))
    ):
        raise ValueError("Expected integer binary label or null")
    expected = {1: "keep", 0: "skip", None: "uncertain"}[label]
    if (
        "action" not in row
        and row.get("provenance", {}).get("version") == "pilot-v0"
        and label is not None
    ):
        return expected
    if row.get("action") != expected:
        raise ValueError("Missing or inconsistent action")
    return expected


def load_rows(path, allow_draft=False):
    payload = path.read_bytes()
    rows = [json.loads(line) for line in payload.splitlines() if line.strip()]
    if not rows:
        raise ValueError("Empty dataset")
    data_sha = hashlib.sha256(payload).hexdigest()
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
        row["action"] = action_value(row)
        for field, allowed in HEAD_LABELS.items():
            if field in row and row[field] not in allowed | {"uncertain"}:
                raise ValueError(f"Invalid {field} label")
        if row["annotation_status"] == "single_human_reviewed_draft":
            if data_sha != FROZEN_SHA:
                raise ValueError(
                    "Reviewed dataset differs from frozen exploratory release"
                )
        elif row["annotation_status"] != "human_reviewed" and not (
            allow_draft
            and row["provenance"].get("version") == "pilot-v0"
            and row["annotation_status"] == "assistant_draft_pending_human_review"
        ):
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
    trainable = [r for r in rows if r["label"] in (0, 1)]
    for split in ("train", "validation", "test"):
        if {r["label"] for r in trainable if r["split"] == split} != {0, 1}:
            raise ValueError(f"Both classes required in {split}")
    return rows


def filter_rows_for_head(rows, head):
    """Keep rows with a known label for one head; preserve the ambiguity set."""
    if head not in HEAD_LABELS:
        raise ValueError(f"Unknown head: {head}")
    if not rows:
        raise ValueError("Cannot filter an empty dataset")
    usable, ambiguous = [], []
    for row in rows:
        value = action_value(row) if head == "action" else row.get(head)
        if value == "uncertain":
            ambiguous.append(row)
        elif value in HEAD_LABELS[head]:
            usable.append(row)
        else:
            raise ValueError(f"Invalid or missing {head}")
    return usable, ambiguous


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
    # Snapshot rows are independent; timestamps do not establish conversation history.
    for i, row in enumerate(rows):
        text = row["candidate_text"]
        extra[i] = [
            min(math.log1p(len(text.split())) / math.log1p(256), 1.0),
            bool(re.match(r"^\s*#{1,6}\s", text)),
            bool(re.match(r"^\s*(?:[-*+] |\d+[.)] )", text)),
            0.0,
        ]
    return np.concatenate([vectors, extra], axis=1).astype(np.float32), texts, truncated


def training_weight(rows):
    labels = [action_value(r) for r in rows if r["split"] == "train"]
    keep, skip = labels.count("keep"), labels.count("skip")
    if not keep or not skip:
        raise ValueError("Training requires both known action classes")
    return torch.tensor([skip / keep], dtype=torch.float32)


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


def validation_baselines(rows, features, texts, labels, train, valid, seed):
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
        logistic = LogisticRegression(max_iter=1000, random_state=seed)
        logistic.fit(values[train], labels[train])
        baseline_scores[name] = logistic.predict_proba(values)[:, 1]
    for name, values in baseline_scores.items():
        t = (
            0.5
            if name in ("store_all", "majority", "rules")
            else select_threshold(labels[valid], values[valid])
        )
        baselines[name] = {"validation": metrics(labels[valid], values[valid], t)}
    return baselines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=Path("data/admission_pilot_v0.jsonl")
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-draft", action="store_true")
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, choices=(0.001, 0.0003), default=0.001)
    parser.add_argument("--dropout", type=float, choices=(0.0, 0.2), default=0.2)
    parser.add_argument("--baselines-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.epochs <= 30:
        parser.error("epochs must be in 1..30 for the pilot")
    source_rows = load_rows(args.data, args.allow_draft)
    development = [r for r in source_rows if r["split"] in ("train", "validation")]
    rows, ambiguity_rows = filter_rows_for_head(development, "action")
    if not rows:
        raise ValueError("No binary action rows available after uncertainty filter")
    assert all(row.get("action", "keep") != "uncertain" for row in rows)
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
        for s in ("train", "validation")
    }
    train, valid = indices["train"], indices["validation"]
    x, y = torch.from_numpy(features), torch.from_numpy(labels).view(-1, 1)
    baselines = validation_baselines(
        rows, features, texts, labels, train, valid, args.seed
    )
    if args.baselines_only:
        result = {
            "baselines": baselines,
            "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
            "train": len(train),
            "validation_keep": int(labels[valid].sum()),
            "validation_skip": int(len(valid) - labels[valid].sum()),
            "seed": args.seed,
            "encoder_revision": REVISION,
            "feature_version": FEATURE_VERSION,
        }
        (args.output / "report.json").write_text(json.dumps(result, indent=2) + "\n")
        return
    model = AdmissionMLP(args.dropout)
    parameter_count = sum(p.numel() for p in model.parameters())
    assert parameter_count == 53953
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.0001)
    positive = float(labels[train].sum())
    negative = float(len(train) - positive)
    if not positive or not negative:
        raise ValueError("Filtered training split must contain both action classes")
    pos_weight = training_weight(source_rows)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    history, best_loss, stale, best = [], float("inf"), 0, None
    for epoch in range(args.epochs):
        model.train()
        order = train[torch.randperm(len(train)).numpy()]
        total = 0.0
        for start in range(0, len(order), 32):
            batch = order[start : start + 32]
            optimizer.zero_grad(set_to_none=True)
            if any(action_value(rows[i]) not in ("keep", "skip") for i in batch):
                raise ValueError("Ambiguous training batch")
            loss = criterion(model(x[batch]), y[batch])
            if not torch.isfinite(loss):
                raise ValueError("Non-finite training loss")
            loss.backward()
            if not all(
                parameter.grad is None or torch.isfinite(parameter.grad).all()
                for parameter in model.parameters()
            ):
                raise ValueError("Non-finite training gradient")
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
    counts = defaultdict(Counter)
    for row in source_rows:
        counts[row["split"] + "/" + row["provenance"]["version"]][row["action"]] += 1
    if ambiguity_rows:
        probe_features, _, _ = build_features(ambiguity_rows, encoder)
        with torch.no_grad():
            probe_scores = (
                model(torch.from_numpy(probe_features)).sigmoid().flatten().tolist()
            )
        (args.output / "development_ambiguity.jsonl").write_text(
            "".join(
                json.dumps(
                    {
                        "example_id": r["example_id"],
                        "split": r["split"],
                        "p_keep": score,
                    }
                )
                + "\n"
                for r, score in zip(ambiguity_rows, probe_scores, strict=True)
            )
        )
    report = {
        "source_action_counts_by_split_batch": counts,
        "status": "pipeline_trial_only",
        "mode": "suggestion_only_not_integrated",
        "annotation_status": sorted({r["annotation_status"] for r in source_rows}),
        "limitations": ["Exploratory fictional data with narrow validation support."],
        "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "encoder": ENCODER,
        "encoder_revision": REVISION,
        "feature_order": FEATURES,
        "feature_version": FEATURE_VERSION,
        "truncation": "256 wordpieces maximum; candidate first, then recent context",
        "truncated_examples": truncated,
        "uncertainty_filter": {
            "head": "action",
            "source_rows": len(development),
            "binary_rows": len(rows),
            "ambiguity_rows": len(ambiguity_rows),
            "ambiguity_ids": [r["example_id"] for r in ambiguity_rows],
            "train_keep": int(positive),
            "train_skip": int(negative),
            "positive_class_weight": float(pos_weight.item()),
            "assertion_no_uncertain_rows_reach_loss": True,
        },
        "parameters": parameter_count,
        "seed": args.seed,
        "device": "cpu",
        "best_epoch": best["epoch"],
        "learning_rate": args.lr,
        "dropout": args.dropout,
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
            "feature_version": FEATURE_VERSION,
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
