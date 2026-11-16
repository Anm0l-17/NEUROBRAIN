"""Paired local smoke evaluation; adaptive results reuse identical routed requests."""

import hashlib
import json
import re
import statistics
import sys
import time
from pathlib import Path

from neurobrain.chat import chat, needs_thinking

ROOT = Path(__file__).resolve().parents[1]


def score(case, answer):
    return (
        all(re.search(p, answer, re.I | re.S) for p in case["required"])
        and not any(
            re.search(p, answer, re.I | re.S) for p in case.get("forbidden", [])
        )
        and len(answer.split()) <= case.get("max_words", 10000)
    )


def main():
    fixture = ROOT / "tests/fixtures/chat_accuracy.json"
    cases = json.loads(fixture.read_text())
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else ROOT / "reports/chat_accuracy_latest.json"
    )
    report = dict(
        scope="Small authored smoke set, one deterministic sample per case/mode; not a general accuracy benchmark.",
        adaptive_measurement="Reuses fast/think result selected by the router; identical request, no additional inference.",
        fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
        modelfile_sha256=hashlib.sha256(
            (ROOT / "ollama/Modelfile").read_bytes()
        ).hexdigest(),
        model="neurobrain-test",
        temperature=0,
        cases=[],
    )
    chat([dict(role="user", content="hello")], "fast")  # Unscored warm-up.
    for index, case in enumerate(cases):
        messages = [dict(role="user", content=case["prompt"])]
        row = dict(case=case, routed_thinking=needs_thinking(messages), results={})
        for mode in ("fast", "think") if index % 2 == 0 else ("think", "fast"):
            start = time.monotonic()
            try:
                result = chat(messages, mode)
                result["passed"] = bool(score(case, result["answer"]))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                result = dict(error=str(exc), passed=False)
            result["seconds"] = round(time.monotonic() - start, 3)
            row["results"][mode] = result
            print(case["id"], mode, result["passed"], result["seconds"], flush=True)
        row["results"]["auto"] = row["results"][
            "think" if row["routed_thinking"] else "fast"
        ]
        report["cases"].append(row)
        path.write_text(json.dumps(report, indent=2) + "\n")
    report["summary"] = {
        mode: dict(
            passed=sum(r["results"][mode]["passed"] for r in report["cases"]),
            total=len(cases),
            median_seconds=round(
                statistics.median(
                    r["results"][mode]["seconds"] for r in report["cases"]
                ),
                3,
            ),
        )
        for mode in ("fast", "think", "auto")
    }
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
