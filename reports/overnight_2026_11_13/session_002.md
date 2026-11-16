# Session 002 — local evidence walkthrough

Initial 60-second extraction timeout did not reproduce on a fresh runner: 3.10 seconds. Runtime logs show overlapping cancelled requests earlier; cause remains unproven. No timeout or service configuration was changed.

Added scripts/demo_observation.py with disposable fictional extraction, persistence, duplicate, restart, current-version citation, absent-evidence, all-version deletion, retained-source and tombstone assertions. The first run exposed unsupported citation output after update. Restricted the citation output schema to current retrieved IDs and retained application validation. Five focused extraction tests pass, including deletion during inference. Two real walkthroughs then passed in 5.110 and 5.173 seconds. This is development smoke evidence, not accuracy or latency benchmarking.

CodeRabbit initial source review completed with seven issues. Focus-delay issue is not applicable: window_probe.swift already waits five seconds before capture. Extraction-change idempotency and cloud read errors are valid and assigned to the next session; source listing and interactive recovery are useful follow-ups. Last-question-only UI and in-flight answer/deletion boundary need explicit handling. Current citation enum fix needs final follow-up review. No deployment or push.
