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

## 13 November overnight — sessions 002 and 003
Local model walkthrough passed twice; extraction citation schema fixed; lifecycle, chat recovery, provenance and controlled cloud errors reviewed and tested. ECC Chrome browser walkthrough passed on fictional temporary data. Reports: reports/overnight_2026_11_13. CodeRabbit review dispositions recorded. No commit because source files contain substantial pre-existing uncommitted user work; no push/deployment.


### TASK-006 — generator pilot, 13 November 2026
Completed 20-step text-only Qwen3.5-4B QLoRA smoke experiment (5 train / 3 development). Baseline loss 2.215, reloaded adapter 1.674. Citation markers improved 1/3 to 3/3, but assistant-to-user attribution regressed in one case. No full-corpus expansion or production promotion. CodeRabbit one path issue fixed and generation rerun matched. Evidence: reports/generator_pilot_v0/RESULTS.md.


### TASK-007 — attribution repair retest completed
17 tiny training examples / 9 development cases; same 20-step settings, fresh adapter. Baseline / previous / repaired combined passes: 4/9, 7/9, 7/9. Repaired adapter fixes confirmed-draft contradiction but fails hospital attribution with repetition and incorrectly attributes financial reflection to user. Overall NO. CodeRabbit 0 issues in evaluation-script review. No scaling/deployment/teacher training. Evidence: reports/generator_pilot_v1/RESULTS.md.
