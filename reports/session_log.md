# NeuroBrain implementation log

## 27 October 2026 — checkpoint C0: first runnable memory baseline

- **Trigger:** professor requires system design plus basic module implementation; user authorized building and saving files to the project path.
- **Input:** `NeuroBrain_Session_Plan.md` revision 27 October 2026 (authoritative schedule); working plan and architecture diagrams as background. Existing planning/research files preserved.
- **Objective:** working deterministic note-memory lifecycle and a presentable design, with clear neural-training status.
- **Implemented:** Python package; directory/input policy; versioned TXT/MD import; exact evidence spans; SQLite/FTS5; lexical retrieval; extractive `ask`; inspection; all-version source deletion; receipts/tombstones; CLI; loopback web controls; fictional fixtures; repeatable temporary-data demo.
- **Session mapping:** partial 01–02, 17–20, 23–24, and thin interfaces brought forward from 43–44. No stage is marked fully complete; datasets, neural training, embeddings, and full stage-C gates remain outstanding.
- **Actual hours:** not measured as a student work session; do not equate automated development elapsed time with the plan's two-hour learning units.
- **Versions/checks/errors:** see `verification.md`. Initial local HTTP test needed additional runtime permission to bind loopback; the permitted run passed. No source-control repository was present, so no commit or diff claim is made.
- **Exit:** basic demonstration works; this is not the final research release.
- **Next prerequisite:** student review of the checkpoint, model/hardware feasibility, and session-07 annotation pilot with reviewed labels before training.

## 2 November 2026 — cloud prototype direction checkpoint

- **Decision:** use Google Drive for original note files and Supabase PostgreSQL for cloud evidence storage; keep SQLite as the tested local reference until parity is demonstrated.
- **Prepared:** cloud setup guide and Supabase schema with per-user row-level security, source versions, chunks, search vectors, tombstones and deletion receipts.
- **Not implemented:** Google OAuth, Drive import, Supabase authentication, cloud `MemoryStore`, migration, or cloud verification tests.
- **Next prerequisite:** create the Supabase project and Drive folder, then implement authenticated cloud import while preserving the existing policy, citation and deletion behavior.

## 2 November 2026 — Step 1 baseline lock and evaluation gate

- **Objective:** establish a repeatable fictional evaluation gate before semantic retrieval or admission-model integration.
- **Implemented:** `data/evaluation_v0.jsonl`, `scripts/evaluate_baseline.py`, `tests/test_evaluation.py`, README usage instructions, and `reports/baseline_v0.json`.
- **Measured baseline:** 5/5 answerable cases retrieved, unsupported-query abstention 1.0, citation validity 1.0, deletion canary removed after forget, and unrelated retained evidence remained available.
- **Verification:** evaluator passed; full unittest suite passed 23/23 with loopback permission; Ruff check and format check passed; Git diff check passed; CodeRabbit reviewed the tracked README change and raised 0 issues.
- **Boundary:** this is a deterministic lexical/extractive lifecycle gate over fictional notes, not evidence of semantic-search quality, temporal reasoning, generation quality, or real-user performance.
- **Next prerequisite:** add the measured semantic-retrieval experiment while preserving this baseline as the regression control.
