"""Admission MLP v2: add LoCoMo keep/skip turns and compare against the logistic baseline.

LoCoMo (CC BY-NC 4.0, snap-research/locomo @ 3eb6f2c) labels: a dialogue turn is
"keep" when a session observation cites its dia_id, otherwise "skip". Those
observations are model-generated, not human labels. Splits are by conversation
(LoCoMo: 7 train / 1 validation / 2 test) and by template family for our reviewed
fictional rows (70/15/15), so no group crosses splits.

Two configurations: `locomo` (LoCoMo train only) and `combined` (LoCoMo + ours).
Each reports, per test source, the MLP and the embedding-logistic baseline at the
validation-chosen threshold.

Run: PYTHONPATH=src:scripts .venv/bin/python scripts/train_admission_v2.py --output reports/admission_v2
"""

import argparse
import hashlib
import json
import random
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

from train_admission import ENCODER, REVISION, AdmissionMLP, build_features, metrics, select_threshold

ROOT = Path(__file__).resolve().parents[1]
LOCOMO = ROOT / ".neurobrain/raw/locomo10.json"
LOCOMO_SHA = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
OURS = ROOT / "data/admission_reviewed_v0_2.jsonl"


def locomo_rows(rng):
    raw = LOCOMO.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == LOCOMO_SHA, "LoCoMo hash mismatch"
    convs = sorted(json.loads(raw), key=lambda c: c["sample_id"])
    order = [c["sample_id"] for c in convs]
    rng.shuffle(order)
    split = {s: "train" for s in order[:7]} | {order[7]: "validation"} | {s: "test" for s in order[8:]}
    rows = []
    for c in convs:
        cited = {
            ref
            for key, obs in c["observation"].items()
            for facts in obs.values()
            for _, refs in facts
            for ref in ([refs] if isinstance(refs, str) else refs)
        }
        for key, turns in c["conversation"].items():
            if not key.startswith("session_") or key.endswith("date_time"):
                continue
            previous = ""
            for t in turns:
                text = t.get("text", "").strip()
                if text:
                    rows.append({
                        "candidate_text": text,
                        "prior_context": previous,
                        "label": int(t["dia_id"] in cited),
                        "split": split[c["sample_id"]],
                        "source": "locomo",
                    })
                previous = text
    return rows


def our_rows(rng):
    rows = [json.loads(line) for line in OURS.open()]
    rows = [r for r in rows if r.get("action") in ("keep", "skip")]
    # Only three template families exist; reuse the v1 assignment (1,422 / 18 / 48).
    split = {
        "assistant-structured-scenarios-a1": "train",
        "assistant-evaluation-source-situations-01-provisional": "validation",
        "assistant-evaluation-source-situations-02-provisional": "test",
    }
    return [{
        "candidate_text": r["candidate_text"],
        "prior_context": r["prior_context"],
        "label": int(r["action"] == "keep"),
        "split": split[r["template_family"]],
        "source": "ours",
    } for r in rows]


def train_mlp(x, y, train, valid, seed, epochs=30):
    torch.manual_seed(seed)
    model = AdmissionMLP(dropout=0.2)
    pos = float((y[train] == 1).sum())
    weight = torch.tensor([(len(train) - pos) / max(pos, 1.0)])
    loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=weight)
    opt = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0001)
    xt, yt = torch.from_numpy(x), torch.from_numpy(y).view(-1, 1)
    best, best_state, gen = -1.0, None, torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        for batch in torch.from_numpy(train)[torch.randperm(len(train), generator=gen)].split(64):
            opt.zero_grad()
            loss_fn(model(xt[batch]), yt[batch]).backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            scores = torch.sigmoid(model(xt[valid])).numpy().ravel()
        ap = metrics(y[valid], scores, 0.5)["average_precision"]
        if ap > best:
            best, best_state = ap, {k: v.clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(xt)).numpy().ravel()


def evaluate(rows, scores, valid, test_sets):
    labels = np.array([r["label"] for r in rows], dtype=np.float32)
    t = select_threshold(labels[valid], scores[valid])
    return {name: metrics(labels[idx], scores[idx], t) for name, idx in test_sets.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    np.random.seed(args.seed)
    torch.set_num_threads(2)
    rows = locomo_rows(rng) + our_rows(rng)
    encoder = SentenceTransformer(ENCODER, revision=REVISION, device="cpu", local_files_only=True)
    x, _, truncated = build_features(rows, encoder)
    y = np.array([r["label"] for r in rows], dtype=np.float32)

    def idx(split, sources):
        return np.array([i for i, r in enumerate(rows) if r["split"] == split and r["source"] in sources], dtype=int)

    tests = {"test_locomo": idx("test", {"locomo"}), "test_ours": idx("test", {"ours"})}
    report = {
        "seed": args.seed,
        "locomo_sha256": LOCOMO_SHA,
        "truncated_inputs": truncated,
        "counts": {
            f"{s}/{src}": {"rows": int(len(idx(s, {src}))), "keep": int(y[idx(s, {src})].sum())}
            for s in ("train", "validation", "test") for src in ("locomo", "ours")
        },
        "note": "LoCoMo labels come from model-generated observations; LoCoMo has only 10 conversations.",
        "configs": {},
    }
    for name, sources in (("locomo", {"locomo"}), ("combined", {"locomo", "ours"}), ("ours_only", {"ours"})):
        train, valid = idx("train", sources), idx("validation", sources)
        mlp = train_mlp(x, y, train, valid, args.seed)
        logistic = LogisticRegression(max_iter=2000, random_state=args.seed).fit(x[train], y[train])
        base = logistic.predict_proba(x)[:, 1]
        report["configs"][name] = {
            "train_rows": int(len(train)),
            "mlp": evaluate(rows, mlp, valid, tests),
            "embedding_logistic": evaluate(rows, base, valid, tests),
        }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, c in report["configs"].items():
        for test in tests:
            print(f"{name:9} {test:12} MLP AP {c['mlp'][test]['average_precision']:.3f} F1 {c['mlp'][test]['f1']:.3f} | "
                  f"logistic AP {c['embedding_logistic'][test]['average_precision']:.3f} F1 {c['embedding_logistic'][test]['f1']:.3f}")
    print(json.dumps(report["counts"]))


if __name__ == "__main__":
    main()
