"""Verify trusted local pilot weights reproduce the saved prediction fixture."""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from train_admission import AdmissionMLP


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    checkpoint = torch.load(
        args.run / "checkpoint.pt", map_location="cpu", weights_only=True
    )
    model = AdmissionMLP()
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    fixture = np.load(args.run / "reload_fixture.npz", allow_pickle=False)
    with torch.no_grad():
        scores = (
            model(torch.from_numpy(fixture["features"])).sigmoid().flatten().numpy()
        )
    error = float(np.max(np.abs(scores - fixture["scores"])))
    result = {
        "fresh_process": True,
        "max_absolute_error": error,
        "tolerance": 1e-6,
        "passed": bool(np.isfinite(error) and error <= 1e-6),
    }
    (args.run / "reload_check.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
