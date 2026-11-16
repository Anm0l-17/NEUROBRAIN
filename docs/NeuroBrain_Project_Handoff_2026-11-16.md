# NeuroBrain Project Handoff

**As of:** 16 November 2026  
**Purpose:** A source-linked handoff for a new human or LLM collaborator. This document separates completed work, measured results, plans, and unresolved work. It is a snapshot, not a claim that every chat exchange is represented.

## 1. Project in one page

NeuroBrain is a privacy-conscious personal-memory assistant. Its intended lifecycle is: ingest user-approved sources, extract candidate facts with evidence and uncertainty, apply hard privacy rules, decide whether a fact should be retained, preserve provenance and temporal scope, retrieve relevant evidence, answer with citations or abstain, and support verifiable forgetting.

There are two separate model efforts:

1. **Admission model:** a small classifier meant to suggest whether a candidate memory is useful. It must never override privacy rules. It is distinct from the answer generator. Its data is fictional and its labels/splits have unresolved independence and quality limits.
2. **Generator adaptation:** Qwen3.5-4B with a small LoRA adapter, focused on evidence-grounded personal-memory answers and ownership attribution. This remains an experiment; neither the adapter nor a prompt change passed the promotion gate.

The repo contains a working deterministic local memory baseline and hybrid retrieval implementation, extensive plans and data-review artifacts, and newer chat, extraction, screen-observation, cloud, and prototype work that is largely **uncommitted and not fully verified**. Do not equate files existing with end-to-end features being accepted.

## 2. Current state (verified from repo on 16 Nov)

| Area | State | Evidence / boundary |
|---|---|---|
| Local deterministic memory | Implemented baseline: TXT/Markdown import, exact evidence spans, SQLite/FTS5, lexical retrieval, extractive answer, inspect, versioned forgetting/tombstones/receipts, CLI and loopback web UI. | Initial implementation and baseline evaluation recorded in `reports/session_log.md`; baseline used fictional notes and is not real-user validation. |
| Hybrid retrieval | Implemented using pinned offline MiniLM embeddings, reciprocal-rank fusion, lexical fallback, citation preservation, cache invalidation and locking. | `reports/session_log.md`; original semantic evaluation was only two paraphrase cases. |
| Cloud direction | Design and Supabase schema/setup are documented; Drive/Supabase authentication, cloud store, migration and parity are not established by the dated log. New cloud files exist in the dirty checkout; treat live integration as unverified. | `docs/Cloud_Setup.md`, `supabase/`, `src/neurobrain/cloud.py`. |
| Admission data | Consolidated reviewed snapshot v0.2: 1,584 authored fictional records (960 keep, 528 skip, 96 uncertain); uncertain actions keep null binary labels. Group/split independence remains a key constraint. | `reports/admission_reviewed_v0_2.md`, `reports/admission_semantic_grouping.md`. |
| Admission training | An exploratory start gate passed on a frozen release, then a small diagnostic and baselines were run. This is not a deployable classifier; fresh independent origins, leakage-safe partitions, trainer fixes and held-out final evaluation remain open. | `reports/admission_start_v1/`, `reports/admission_baselines_v1/`, `docs/NeuroBrain_Session_Plan.md`. |
| Generator compact run | Kaggle Qwen3.5-4B NF4 LoRA, 20 updates, 13 adaptations across 12 personas, one T4. Adapter reloaded. On old 9-case development: base 6/9, adapter 8/9. | `reports/compact_kaggle_v1/RESULTS.md`. Adapter failed due to false ownership of a fictional vineyard. |
| Attribution follow-up | Expanded instruction: adapter 9/9 on old nine but 4/6 on new probes; it newly attributed a fictional radio narrator's occupation to the author and still failed courier residence. Prompt not promoted. | `reports/attribution_followup/RESULTS.md`. |
| Candidate retraining | Eight proposed hard training rows and six final evaluation rows were prepared. A subsequent Kaggle attempt failed before training with `NameError: original is not defined`; no new adapter was saved. Keep the six final examples held out. | `data/neurobrain_shortlist_v1/attribution_hard_train.jsonl`, `attribution_final_eval.jsonl`; original failure is noted in the active handoff context, not yet a standalone report. |
| Prototype/demo | A 23 November acceptance plan and runbooks exist. Readiness audits and live observation work show integration gaps. Do not claim the supervised multi-app prototype is accepted until its actual acceptance path is rerun and evidenced. | `docs/Prototype_23_November_Plan.md`, `docs/Prototype_Demo_Runbook.md`, `reports/Prototype_Readiness_2026_11_13.md`. |
| Git/worktree | Tracked files are modified and many new files are untracked. Recent commits include compact Kaggle result, attribution follow-up and train/eval rows. No commit/push was performed for this handoff. | `git status` showed extensive existing work before this document was added. Preserve all of it. |

### Important measured outcomes

- Compact Kaggle run: adapter 8/9 versus base 6/9 on the original development suite. The adapter still failed the fictional vineyard ownership case, so the declared gate (9/9 and improvement) failed.
- Follow-up attribution probes: with the original instruction both base and adapter passed 5/6 new probes; both failed the fictional courier residence. With an expanded instruction, adapter scored 9/9 on the original suite but only 4/6 new probes; the expanded instruction introduced a radio narrator ownership error. Do not select prompts on the old suite alone.
- Both forget probes were answered correctly in the follow-up, but this did **not** test deletion from storage, indexes, caches, backups, or retrieval after restart.
- Admission start gate / baseline results are exploratory and trained on small, synthetic/reviewed data. They are not evidence of reliable real-world automatic memory decisions.

## 3. Recorded work sessions, in chronological order

This timeline is reconstructed from Git history and `reports/session_log.md` / `.agent/logs/LOG.md`. The project log is detailed for some periods and sparse for others; “session” below means a recorded work checkpoint, not a complete transcript of every conversation.

### 27 October — first runnable baseline (checkpoint C0)

Built the Python local-memory baseline: TXT/Markdown source policy and import, evidence spans, SQLite/FTS5, lexical retrieval, extractive ask, inspection, source-version deletion, receipts/tombstones, CLI, loopback web controls, fictional fixtures and repeatable demo. Neural training, embeddings and full stage-C acceptance were not complete. The project log explicitly says actual student hours were not measured.

### 2 November — cloud direction and deterministic evaluation

Chose Google Drive for original note files and Supabase PostgreSQL for cloud evidence, keeping SQLite as the tested local reference. Wrote setup/schema material; cloud auth/import/store/parity were still planned. Locked a fictional lexical/extractive baseline: 5/5 answerable retrieval, 1.0 unsupported-query abstention, 1.0 citation validity, and deletion canary removed while unrelated evidence remained. These scores only cover the small deterministic fixture.

### 3 November — hybrid retrieval and review preparation

Added offline MiniLM embeddings, a rebuildable semantic index, reciprocal-rank fusion, CLI/web paths, lexical fallback, citation retention, deletion cache invalidation and locking. Reported lexical Recall@5 1.0 and semantic Recall@5 1.0 on two fictional paraphrases; not enough to claim broad semantic gains. Prepared blind review material for the 80-row admission pilot. No completed independent pilot review or model training was claimed in that preparation entry.

### 4–6 November — admission pilot review and Stage A learning

Reviewed/adjudicated pilot labels and added annotation rules, repeat-review artifacts and scoring. Stage A teach-back established a correct explanation of the admission MLP, grouped split leakage and source-scoped forgetting after feedback, but other learner exercises were still unrecorded. Pilot records remained drafts/small-data evidence, not a finished training set.

### 6 November — Qwen candidate and project materials

Documented Qwen3.5-4B as a generator candidate, added review materials, pilot review workbooks and Stage A closure material. The Qwen base was a frozen local candidate; this did not constitute a trained NeuroBrain generator.

### 7–8 November — admission corpus batches and review

Created and reviewed fictional Batch A and Batch B candidates, then Batch C, with blind review, rationales and proposed resolutions. Batch A/B shared a template family; avoid treating authored row count as independent source count. User corrections and uncertainty handling were kept in separate adjudication files. The corpus process preserved uncertain cases with null binary targets and kept original submissions intact. No trustworthy independent final split was established at this point.

### 8–9 November — consolidated admission snapshot and exploratory gates

Accepted corrections into v0.1 then v0.2; v0.2 contains 1,584 records and 96 uncertain actions. Semantic-origin screening found shared template/scenario relationships, including a connected 1,500-row component, so the existing authored pool did not provide independent validation/test origins under the origin rule. A frozen exploratory start gate passed for its release; diagnostic fitting showed finite gradients, parameter changes, and repeatable reload. The baseline report used 1,422 train binary labels, 12 keep and 6 skip validation cases, while 48 known test labels and 12 ambiguity probes stayed reserved. The tiny validation set and origin dependence restrict all conclusions.

### 9 November — fresh evaluation tranches and prototype plan

Prepared/reviewed fresh fictional tranches, including sensitivity corrections and a consolidated snapshot. Origin independence and split assignment remained open. A 23 November prototype plan was written. The environment test check found one real uncertainty-selector failure (and a socket-permission issue resolved in a separate permitted rerun): 34 passing, one unresolved failure in that dated report. Trainer audit flagged mixed label handling, action/label consistency, inferred history, missing ambiguity score and test metrics during model search. These were findings/scheduled fixes, not proof they were all fixed later.

### 10–13 November — runtime, chat, extraction and readiness work

Repo contains chat accuracy/holdout/runtime reports, extraction smoke reports, observation and prototype work, and readiness audits from this period. They should be read as separate task-specific evidence. The 13 November readiness audit estimated the supervised prototype at roughly 60%; hosted persistence and live cross-app observation were not established. On-device/runtime context and some requests timed out; do not claim unverified integrations. See `reports/Chat_Accuracy_2026_11_13.md`, `reports/Progress_Report_2026_11_13.md`, `reports/Prototype_Readiness_2026_11_13.md` and dated JSON reports.

### 14 November — compact data shortlist and Kaggle QLoRA

Reviewed a compact admission ID shortlist and curated a separate small generator set from PersonaMem-v2. Source notes pin intended role/license and exclusions; selected only 13 adaptations across 12 personas. The full eligible source pool was not semantically reviewed. Kaggle T4 training completed 20 QLoRA updates, adapter reload succeeded, peak allocated memory 10.64 GiB, adapter 3,674,248 bytes. Base 6/9, adapter 8/9 on the then-current dev suite. Main known failure was attributing a fictional vineyard owner's fact to the user. The code review also found standalone script hashes depended on notebook globals; packaging was repaired after training, so the trained run predates that packaging fix. Results: `reports/compact_kaggle_v1/RESULTS.md`.

### 16 November — attribution probes and attempted next training step

Added six paired attribution/forget probes and recorded base/adapter results under original and expanded instructions. Expanded instruction improved the old adapter set but regressed on new ownership cases; decision was to keep it experimental. Eight hard train examples and six separate final evaluation examples were drafted. The next Kaggle training cell did not start because notebook state lacked `original` (`NameError: original is not defined`); no candidate training result exists. Fix the notebook setup as a self-contained sequence before retrying, and keep final-eval examples untouched until model/prompt selection is complete.

### Git milestones (source-control history)

- `7969eed` — initial prototype, research, admission pilot (29 Oct).
- `6554ad9`, `ea504be`, `0e2dd79` — user guide, architecture and cloud plan updates (2 Nov).
- `5d8c63b` — baseline evaluation / Ralph workflow (3 Nov).
- `09ae9c3` — hybrid semantic retrieval (3 Nov).
- `822572a`, `b9aac33` — Qwen candidate and project/review materials (6 Nov).
- `5bd75f0` — compact shortlist and Kaggle adapter evaluation (14 Nov).
- `56717e0` — attribution follow-up evaluation (16 Nov).
- `70a378b` — attribution hard-train and final-eval examples (16 Nov).

Git history is not the same as the current full worktree: substantial later work remains uncommitted/untracked. Review `git status` before any Git operation.

## 4. Product architecture and boundaries

The intended system flow is documented in `docs/NeuroBrain_Architecture.mmd` and `docs/NeuroBrain_Working_Plan.md`:

1. User selects a source; path and privacy rules are enforced before processing.
2. Extract candidate facts with exact evidence, source, time, speaker/owner, confidence and uncertainty.
3. Apply hard privacy and explicit user instructions first.
4. Use the admission classifier only as a suggestion/decision aid, never as an override of privacy or a substitute for confirmation where needed.
5. Store provenance and source-to-derived-artifact links.
6. Retrieve lexical, semantic and temporal evidence; answer with citations or abstain.
7. On forget, remove source-derived records from primary storage and every cache/index/derived artifact, issue a receipt and test residual retrieval after restart.

The currently proven local baseline is narrower than this target. A “forget” instruction answered correctly by Qwen is not equivalent to application memory deletion. Similarly, a citation marker does not prove that attribution is correct.

## 5. Work remaining, ordered by stages

### Stage 0 — preserve and establish the active checkpoint (next)

- Do not clean, reset, stash or overwrite the current worktree; it has substantial user work.
- Read `git status`, inspect the actual Kaggle notebook state and adapter output, and record which environment/kernel is active.
- Repair the failed candidate cell with explicit initialization/loading for all variables (`original`, paired cases, base model, tokenizer, adapter, prompt and evaluation helpers). Make the cell sequence reproducible from a fresh kernel.
- Confirm the attempted cell did not create partial outputs or overwrite the existing compact adapter; save the candidate under a new name/path.
- Run a syntax/import/small-batch smoke on train rows only before launching the 8-row candidate training. Record hashes, base revision, package versions, seed, parameters, checkpoint path, elapsed time and GPU memory.

### Stage 1 — generator attribution experiment

- Keep the existing six follow-up probes as development regressions and the six `attribution_final_eval.jsonl` cases frozen until candidate selection.
- Train one small candidate on `attribution_hard_train.jsonl` only after checking every target is supported by its input and persona/situation separation is clean. Do not use the final-eval targets for prompt or training changes.
- Compare base, original compact adapter, and new candidate under identical decoding and inputs. Score evidence support, correct owner, directness/abstention, and citation separately; include original nine and follow-up six.
- Inspect each error, add only evidence-backed training examples/instructions, and repeat against development cases. Hard instructions alone are not a pass if they move errors to new ownership types.
- After selecting, evaluate once on the frozen final set. Do not promote unless predeclared thresholds pass; report uncertainty from the small sample. Do not claim broad personalization or real-user quality.

### Stage 2 — admission data and trainer integrity

- Resolve the recorded trainer defects, especially uncertainty filtering (historically expected 79 usable cases but returned 0), explicit action/label consistency, feature/history leakage, and ensuring test metrics are not used during model selection.
- Preserve null labels for uncertain examples; exclude them from binary loss/primary binary metrics while keeping them for a separate uncertainty analysis.
- Obtain genuinely independent scenario/source origins, freeze grouped partitions and hashes before fitting. Existing 1,584 authored rows are not 1,584 independent origins.
- Compare simple baselines before the MLP. Keep privacy as a deterministic hard override. Require reproducible checkpoint reload, feature parity, finite gradients, calibration/threshold selection on validation only, and a final untouched test.
- Do not enable automatic omission until an independently reviewed benefit/safety gate passes. Suggestion mode with user review is the conservative fallback.

### Stage 3 — deterministic app and deletion acceptance

- Rerun the baseline suite and expand it beyond tiny fictional fixtures, preserving known good behavior as regression tests.
- Trace deletion across primary rows, versions, embeddings, FTS/semantic indexes, caches, exports, backups/cloud replicas and receipts. Verify after restart that forgotten evidence cannot be retrieved; document retention/receipt semantics.
- Test malformed inputs, excluded paths, symlinks, prompt injection, unsafe Markdown, web mutations, concurrent operations, restart/recovery, citation validity and abstention.
- Keep SQLite as the known local reference until Drive/Supabase auth, ownership, row-level security, migration, deletion parity and failure recovery are demonstrated end-to-end.

### Stage 4 — prototype integration and demo

- Follow `docs/Prototype_23_November_Plan.md` and `docs/Prototype_Demo_Runbook.md` acceptance criteria. Verify approved source selection, live observation/OCR, typed evidence, citations, no duplicate saving, privacy/forget flow and persistence in a fresh session.
- Clearly distinguish the deterministic app path from unverified observation/cloud adapters and from offline model experiments.
- Capture a fresh end-to-end evidence bundle (inputs, expected output, actual output, citations, deletion proof, environment and known limits). A plan, unit test, server startup, or timed-out live run is not end-to-end acceptance.

### Stage 5 — release, documentation and GitHub

- Update the README and model cards with exact supported behavior, data provenance/licensing, base model + adapter disclosure, measured task limits and known failures.
- Run the project’s applicable tests after the current dirty work is understood; report each pass/fail/blocked/not-run check separately.
- Review all untracked/modified files and secrets/data exclusions. Preserve datasets and weights according to current `.gitignore` and privacy policy.
- Only then prepare a scoped commit and push when the user explicitly requests it. No push is part of this handoff task.

## 6. Immediate resume instructions for the next collaborator

1. Open this handoff and `reports/attribution_followup/RESULTS.md`.
2. Inspect `git status` and keep the existing dirty work untouched.
3. In the Kaggle notebook `anm0l17/gpu-server`, restart or inspect the kernel. Load the exact original nine development prompts from the recorded compact run, plus the six follow-up cases, into explicit variables; do not assume notebook globals survived.
4. Verify the compact adapter checksum against the saved artifact before using it. Save any new candidate separately.
5. Run a one-batch dataset/schema/model-forward smoke; make sure the eight hard train records are the only new target data seen by the optimizer.
6. Train/evaluate only on development first. Keep `attribution_final_eval.jsonl` sealed until candidate selection.
7. Record success or exact failure in a new dated report, including complete generated answers and per-case scores. Never silently overwrite a previous result.

If Kaggle access/session is unavailable, continue with local code/data integrity and test-harness preparation; do not claim training happened.

## 7. Data, privacy, provenance and experiment rules

- Keep admission data and generator data separate. Admission labels are not a generator fine-tuning corpus.
- Preserve source URL/revision/license, file hashes, derivation, filters, exclusions and split group for every training/evaluation record.
- Keep benchmark gold answers and final evaluation targets out of training and prompt iteration.
- Do not use real personal notes in a remote training run without a specific, informed authorization and an approved data minimization plan. The user previously approved the 22 listed examples for Kaggle; that approval is scoped to those examples and the stated run, not arbitrary new data.
- Keep uncertain labels unresolved; do not coerce ambiguity into a binary class.
- Treat source ownership, quoted/fictional content and assistant-authored dialogue as first-class attribution dimensions.
- A correct citation ID can still support the wrong conclusion; score semantic support and owner separately.
- Keep model weights, adapters, training data and application memory distinct. Model training is not memory storage and does not provide deletion/unlearning of facts from weights.

## 8. Key files to read first

- Project and execution roadmap: `README.md`, `docs/NeuroBrain_Session_Plan.md`, `docs/NeuroBrain_Working_Plan.md`
- Architecture and cloud boundary: `docs/NeuroBrain_Architecture.mmd`, `docs/Cloud_Setup.md`
- Admission policy and status: `docs/Admission_Annotation_Guide_v1_2.md`, `reports/admission_reviewed_v0_2.md`, `reports/admission_semantic_grouping.md`, `reports/admission_start_v1/report.json`, `reports/admission_baselines_v1/report.json`
- Generator readiness and results: `docs/Generator_Training_Readiness.md`, `data/neurobrain_shortlist_v1/SOURCES.md`, `reports/compact_kaggle_v1/RESULTS.md`, `reports/attribution_followup/RESULTS.md`
- Pending generator cases: `data/neurobrain_shortlist_v1/attribution_hard_train.jsonl`, `attribution_followup_dev.jsonl`, `attribution_final_eval.jsonl`
- Prototype acceptance: `docs/Prototype_23_November_Plan.md`, `docs/Prototype_Demo_Runbook.md`, `reports/Prototype_Readiness_2026_11_13.md`
- Recorded timeline: `reports/session_log.md`, `.agent/logs/LOG.md`

## 9. Known limits of this handoff

The repo’s dated session log is detailed but not a transcript of every Codex conversation, and some work after 9 November is represented primarily by artifacts/reports rather than a single chronological narrative. The active Kaggle `NameError` is captured from the current continuation context and should be reproduced/confirmed against the notebook before retrying. This document has not itself run project tests, connected to Kaggle, independently reviewed every dataset row, or validated all current uncommitted code.
