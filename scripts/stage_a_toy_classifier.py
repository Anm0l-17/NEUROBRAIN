"""Tiny isolated PyTorch exercise for Stage A; uses synthetic data only."""

from __future__ import annotations

import json

import torch
from torch import nn


def run() -> dict:
    torch.manual_seed(7)
    x = torch.tensor([[-2.0], [-1.0], [1.0], [2.0]])
    y = torch.tensor([[0.0], [0.0], [1.0], [1.0]])
    model = nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.2)
    loss_fn = nn.BCEWithLogitsLoss()
    losses = []

    for _ in range(80):
        logits = model(x)
        loss = loss_fn(logits, y)
        optimizer.zero_grad()
        loss.backward()
        assert all(
            parameter.grad is not None and torch.isfinite(parameter.grad).all()
            for parameter in model.parameters()
        )
        optimizer.step()
        losses.append(float(loss.detach()))

    with torch.no_grad():
        probabilities = model(x).sigmoid().flatten()
    assert losses[-1] < losses[0]
    assert probabilities[0] < 0.5 and probabilities[-1] > 0.5
    return {
        "seed": 7,
        "synthetic_examples": len(x),
        "initial_loss": losses[0],
        "final_loss": losses[-1],
        "loss_decreased": losses[-1] < losses[0],
        "gradients_finite": True,
        "probabilities": [float(value) for value in probabilities],
        "passed": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
