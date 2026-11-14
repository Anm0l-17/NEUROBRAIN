"""Run reviewed training-only mechanical checks before model selection."""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from scripts.freeze_admission_grouped_exploratory import freeze
from scripts.train_admission import (
    ENCODER,
    FEATURE_VERSION,
    HEAD_LABELS,
    REVISION,
    AdmissionMLP,
    build_features,
    filter_rows_for_head,
    load_rows,
    training_weight,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    out = parser.parse_args().output
    root = Path(__file__).resolve().parents[1]
    data, _, manifest = freeze(root)
    rows = load_rows(data)
    counts = defaultdict(Counter)
    for row in rows:
        counts[row["split"] + "/" + row["provenance"]["version"]][row["action"]] += 1
    unknown = {h: len(filter_rows_for_head(rows, h)[1]) for h in HEAD_LABELS}
    assert unknown == dict(action=96, type=95, scope=95, sensitivity=13)
    train = [r for r in rows if r["split"] == "train"]
    known, probes = filter_rows_for_head(train, "action")
    weight = training_weight(rows)
    assert (
        weight.equal(training_weight(train)) and abs(weight.item() - 504 / 918) < 1e-6
    )
    assert len(known) == 1422 and len(probes) == 78
    tiny = known[:16]
    assert {r["action"] for r in tiny} == {"keep", "skip"}
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    encoder = SentenceTransformer(
        ENCODER, revision=REVISION, device="cpu", local_files_only=True
    )
    features, texts, _ = build_features(tiny, encoder)
    raw = [{k: r[k] for k in ("prior_context", "candidate_text")} for r in tiny]
    single, text, _ = build_features(raw[:1], encoder)
    reverse, rt, _ = build_features(raw[::-1], encoder)
    np.testing.assert_allclose(features, reverse[::-1], atol=1e-6)
    np.testing.assert_allclose(features[:1], single, atol=1e-6)
    assert text == texts[:1] and rt[::-1] == texts and not features[:, -1].any()
    _, clipped, n = build_features(
        [dict(prior_context="old " * 400 + "recent", candidate_text="keep marker")],
        encoder,
    )
    assert n == 1 and "recent" in clipped[0] and clipped[0].endswith("keep marker")
    assert len(encoder.tokenizer.encode(clipped[0])) <= min(256, encoder.max_seq_length)
    x = torch.from_numpy(features)
    labels = torch.tensor([r["label"] for r in tiny], dtype=torch.float32).view(-1, 1)
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=weight)
    out.mkdir(parents=True, exist_ok=False)
    results = {}
    for control in ("reviewed", "permuted"):
        torch.manual_seed(17)
        model = AdmissionMLP()
        initial = model[0].weight.detach().clone()
        y = labels if control == "reviewed" else labels[torch.randperm(len(labels))]
        assert control == "reviewed" or not torch.equal(y, labels)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
        model.eval()
        before = criterion(model(x), y).item()
        for _ in range(32):
            model.train()
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            assert torch.isfinite(loss)
            loss.backward()
            assert all(
                p.grad is not None and torch.isfinite(p.grad).all()
                for p in model.parameters()
            )
            optimizer.step()
        model.eval()
        with torch.no_grad():
            after = criterion(model(x), y).item()
            scores = model(x).sigmoid().flatten().numpy()
        assert (
            np.isfinite(after) and after < before and not initial.equal(model[0].weight)
        )
        results[control] = {"initial_loss": before, "final_loss": after}
        if control == "reviewed":
            torch.save(
                {"state_dict": model.state_dict(), "feature_version": FEATURE_VERSION},
                out / "checkpoint.pt",
            )
            np.savez(out / "reload_fixture.npz", features=features, scores=scores)
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts/verify_admission_checkpoint.py"),
            str(out),
        ],
        check=True,
    )
    report = dict(
        results=results,
        reload=json.loads((out / "reload_check.json").read_text()),
        train_ids=[r["example_id"] for r in tiny],
        train_weight=weight.item(),
        counts_by_split_batch=counts,
        unknown_by_head=unknown,
        seed=17,
        steps=32,
        optimizer="AdamW lr=0.001 weight_decay=0.0001",
        encoder_revision=REVISION,
        feature_version=FEATURE_VERSION,
        feature_sha256=hashlib.sha256(features.tobytes()).hexdigest(),
        dataset_sha256=manifest["dataset_sha256"],
    )
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
