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

## 3 November 2026 — Step 2 hybrid semantic retrieval checkpoint

- **Implemented:** pinned offline MiniLM embeddings, rebuildable semantic index, reciprocal-rank-fusion hybrid retrieval, CLI `hybrid` command, web `/api/hybrid` route, lexical fallback, citation preservation, cache invalidation on deletion, and concurrency locking.
- **Measured:** lexical Recall@5 1.0; semantic Recall@5 1.0 on two fictional paraphrase cases. This is a working retrieval path, not evidence of semantic improvement.
- **Verification:** full unittest suite 30/30 passed; Ruff check/format passed; semantic experiment ran offline; Ralph shell checks passed; CodeRabbit raised 0 issues.
- **Status:** Step 2 complete as an evaluated implementation checkpoint. Next work is expanding the held-out evaluation corpus and measuring at larger scale before changing defaults.

## 3 November 2026 — Stage B sessions 07–08 review preparation

- **Objective:** inspect the existing fictional 80-row admission pilot and prepare independent label review without claiming Stage A learner sign-off.
- **Input:** `data/admission_pilot_v0.jsonl`, SHA-256 `f276358074504f4ca76167d34c5162e597b42c83f294384a104894c995e5fa2a`; session plan Stage B revision 27 October 2026.
- **Work:** wrote `docs/Admission_Annotation_Guide.md` and generated a label-free CSV review sheet; recorded group, duplicate and lexical-cue screening in `reports/stage_b_pilot_review_prep.md`.
- **Actual hours:** not measured as a student learning session.
- **Exit:** draft pilot and review materials prepared; no human label review completed. Stage A learner teach-back and Stage B session 08 adjudication remain prerequisites for scaling to session 09.
- **Follow-up:** added a provisional five-field draft-label table, expanded the blind template, and prepared an agreement scorer for two completed human reviews. The guide is still provisional; no adjudication or additional model training occurred.

## 4 November 2026 — Stage B pilot review handoff check

- **Objective:** make the two-review agreement summary interpretable before human annotation.
- **Input:** provisional guide, 80-row blind template and draft-label table from 3 November.
- **Work:** agreement now reports a separate definite-label denominator for type and scope; the scorer rejects the same review file supplied twice and notes that independence must be established by the reviewers.
- **Verification:** seven focused unit tests passed; Ruff check and format check passed; diff whitespace check passed.
- **Actual hours:** not measured as a student session.
- **Exit:** review packet ready; the two independent human sheets, disagreement adjudication, Stage A learner teach-back and v1 guideline freeze remain open. No data expansion or training was performed.

## 6 November 2026 — Stage B single-review inspection

- **Objective:** inspect the user's completed 80-row pilot workbook and derive guideline gaps.
- **Input:** `admission_pilot_v0_blind_review (1).xlsx`, SHA-256 `649f580cd2d0ec6a2f27c470d8f1e67d1ff75ef8efc7951243d939f2e69e8396`.
- **Work:** verified all IDs, unchanged source text, allowed labels and rationales; compared each field with assistant drafts; recorded 14 rows with field differences and revised the provisional guide for the solo-review workflow.
- **Observed:** action 80/80, type 74/80, scope 73/80, sensitivity 72/80, source 80/80 versus drafts. These are descriptive matches, not independent human agreement; see `admission_pilot_review_2026-11-06.md`.
- **Actual hours:** not measured as a student session.
- **Exit:** workbook complete; human adjudication, repeat sample, guideline freeze and Stage A learner teach-back remain open. No training or dataset expansion occurred.
- **Accepted follow-up:** user accepted all 14 proposed resolutions. Saved versioned labels with reasons in `data/admission_pilot_v1_labels.csv` while keeping `status=draft`; froze v1 annotation rules; prepared a 20-row masked-label repeat sheet covering all 16 scenario groups. Repeat review and Stage A learner teach-back remain open before expansion. The original workbook and pilot JSONL were preserved.
- **Repeat follow-up:** user supplied all 20 selected rows. Nineteen matched v1 across all label fields; `pilot-03-02` repeated `project` scope. Saved the submitted CSV, a v1.1 label file with that scope, and a v1.1 guide clarifying correction scope. All pilot labels remain drafts; Stage A learner teach-back and larger human-reviewed data remain open.
