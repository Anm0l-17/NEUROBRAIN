# Ralph Progress Log

Project-local setup prepared. No development tasks defined.

## 2026-11-03 — Task 001 opened

- Defined the semantic-retrieval experiment PRD and acceptance criteria.
- Confirmed the pinned MiniLM model loads offline with 384-dimensional embeddings.
- Next action: implement the experiment while keeping lexical retrieval as the control.

## 2026-11-03 — Task 001 semantic slice

- Implemented a rebuildable in-memory semantic index using the pinned offline MiniLM encoder.
- Added a two-case paraphrase comparison and generated `reports/semantic_v0.json`.
- Measured lexical Recall@5: 1.0; semantic Recall@5: 1.0. This is an initial result, not evidence of improvement.
- Added restart/deletion coverage; task remains open until fallback behavior and a stronger evaluation set are implemented.

## 2026-11-03 — Task 001 complete

- Added hybrid reciprocal-rank-fusion retrieval to the CLI and web API with a cached, refreshable local semantic index.
- Added explicit lexical fallback when the pinned model is unavailable, citation-preserving results, cache invalidation on forget, and concurrent-access locking.
- Final measured result on the two-case fictional paraphrase set: lexical Recall@5 1.0; semantic Recall@5 1.0. No improvement claim is justified yet.
- Verification: 30/30 tests, Ruff clean, offline model load passed, shell/Ralph checks passed, and CodeRabbit raised 0 issues.
- Ralph loop was attempted but stopped because Codex authentication was unavailable inside its Docker sandbox; the task was completed directly in the host checkout.
