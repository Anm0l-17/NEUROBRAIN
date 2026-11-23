# NeuroBrain implementation log

## 9 November 2026 — exploratory admission handoff to Stage D

The prototype admission start gate passed on the frozen exploratory release.
The 18 canonical source hashes, v0.2 bytes, reconstructed records, split file
and split report matched. The historical pilot stayed excluded. Its 80 records
screened against all 1,584 reviewed rows yielded zero normalized exact candidate
or context matches. At candidate cosine ≥0.85 one pair flagged (pilot-01-02 and
batch-a-23-17, 0.874, both describe lost focus after closing a dialog). At
context cosine ≥0.90 none flagged. This pair connects pilot material to training.
The six fresh02 scenarios share a fixed class pattern, limiting the claim.

The reviewed run used 16 training examples for 32 diagnostic steps per condition.
The frozen encoder produced matching individual and batch features, including
after reversing the rows. Known-label and permuted-label loss fell, all gradients
were finite, parameters changed and the fresh process reproduced the reviewed
scores exactly. The permuted run shows that the head can fit arbitrary labels.
See `reports/admission_start_v1/report.json` for IDs, weights, configuration,
hashes and counts. The exact frozen dataset is admitted for exploratory fitting
while preserving single-review annotation status. Any changed release needs a
new review of its hash and provenance.

Stage D opened with all five validation baselines. See
`reports/admission_baselines_v1/report.json`. Train used 1,422 binary targets,
validation used 12 keep and 6 skip. The embedding logistic baseline retained
all 12 useful cases and suggested keeping 4 of the 6 skips. The final 48 known
test labels and 12 final ambiguity probes remain reserved for frozen selection.
Next is the bounded MLP comparison in the Session Plan. Broader Stage B QA,
deletion and external benchmark work continues under the research roadmap.


## 9 November 2026 — plan for 23 November prototype deadline

- Added `docs/Prototype_23_November_Plan.md` with pre-training blockers, dated milestones, local suggestion-mode prototype scope, release tests and fallback decisions. Linked it from the full Session Plan; broader research completion is not claimed.
- Rechecked project-environment tests: 35 discovered, 33 passed initially, one uncertainty selector failure and one socket-permission error. The HTTP case passed on a separate permitted rerun, leaving 34 passing tests and one real unresolved failure. No optional tests were skipped in this environment.
- Inspected the trainer: mixed legacy/action labels can be silently excluded, action/label consistency is not checked, cross-row snapshot history is inferred, ambiguity scoring is not implemented and test metrics currently run during model search. These are scheduled fixes, not completed changes.
- Immediate next implementation is the selector/history fixes with tests, alongside the evaluation-origin and frozen-split decision. No training or prototype feature implementation occurred in this planning turn.

## Fresh evaluation tranche 02 accepted; consolidated snapshot v0.2

- User accepted all four proposed corrections: three person scopes for recurring habits/preferences and restricted sensitivity for the explicit privacy request. Saved a separate 60-row adjudicated snapshot; only those four fields changed.
- Assembled v0.2 with 1,584 records: 960 keep, 528 skip, 96 uncertain actions. Preserved v0.1 and the original submission. Every uncertain action retains a null binary label; all splits remain unassigned.
- Origin assessment, further collection addressing template cues, grouped split freezing and release checks remain pending. No training performed. See `reports/admission_reviewed_v0_2.md`.

## Fresh evaluation tranche 02 — submitted review validated

- Preserved all 60 submitted rows with unchanged cells; draft IDs, contexts, candidates, vocabularies, nonempty rationales and review decisions all validated. Counts: 30 keep, 18 skip, 12 uncertain; 13 rows differ from assistant suggestions on other fields.
- Proposed three scope corrections to person for recurring habits/preferences and one restricted sensitivity for the explicit privacy request. Other submitted differences are retained. Proposals remain pending; no canonical labels or prior snapshots overwritten.
- Coverage is now 1,584 reviewed authored records. The next snapshot follows resolution. Recorded recurring authoring slots as an evaluation limitation to address before more collection. See `reports/admission_eval_fresh_02_review.md`.

## Reviewed snapshot v0.1 and fresh evaluation tranche 02

- Consolidated 1,524 reviewed records, accepted label corrections and notes into `data/admission_reviewed_v0_1.jsonl`. Recorded 930 keep, 510 skip and 84 uncertain actions; each label field retains its own unresolved state. Normalized historical status metadata only in the new snapshot.
- At the user's selection, continued assistant-authored fictional sources: 60 new candidates in six situations, with a blank review CSV and separate suggestions. No exact candidate duplicates or semantic flags against reviewed records at the existing thresholds; independence remains provisional.
- Assembly and grouping tests passed. All splits remain unassigned. Next is the 60-row human review, followed by origin assessment and remaining collection work; no model training occurred. See `reports/admission_reviewed_v0_1.md` and `reports/admission_eval_fresh_02.md`.

## Fresh evaluation tranche 01 — sensitivity adjudication accepted

- User accepted personal sensitivity for family attribution and precise availability, and restricted sensitivity for the explicit privacy request.
- Saved `data/admission_eval_fresh_01_adjudicated.csv` separately from the submitted review. Only three sensitivity fields changed; all 24 rows have draft status and retain submitted notes/rationales. Actions remain 12 keep, 6 skip, 6 uncertain; sensitivities are 20 ordinary, 2 personal, 1 restricted, 1 uncertain.
- Solo review/adjudication milestone complete; independent origin and split design remain open. See `reports/admission_eval_fresh_01_review.md`.

## Fresh evaluation tranche 01 — completed user submission

- Preserved all 24 submitted CSV rows in `data/admission_eval_fresh_01_review_completed.csv`; IDs, source text, vocabulary, rationales and review-decision checks passed.
- Submitted counts: 12 keep, 6 skip, 6 uncertain; nine rows differ from assistant suggestions. User-review coverage is now 1,524, with three sensitivity resolutions pending for this tranche.
- Retained the user's conservative ambiguity judgments. Proposed personal sensitivity for the family attribution and precise availability, and restricted sensitivity for the explicit privacy request, under guide v1.2. Submission unchanged; see `reports/admission_eval_fresh_01_review.md`. Origin independence and split assignment remain outstanding.

## 9 November 2026 — fresh evaluation candidate tranche 01

- Prepared 24 fictional candidates across six source situations and a blank CSV review sheet; assistant suggestions remain separate. All statuses are draft and splits unassigned.
- Verified IDs, review text, blank review fields and exact candidate uniqueness. Offline MiniLM screening flagged no pairs against A/B/C or across new scenarios at candidate 0.85/context 0.90 thresholds. Source independence remains unverified; final test origins remain outstanding.
- Next is solo review of this first tranche before expanding the authoring approach. Total authored 1,524; user-reviewed coverage 1,500. See `reports/admission_eval_fresh_01.md`.

## 9 November 2026 — admission semantic screen and origin grouping

- **Completed:** offline pinned MiniLM screen of all 1,500 reviewed A/B/C candidates and contexts, with 14 source hashes, pair evidence and grouping assignments in `reports/admission_overlap/`.
- **Found:** three cross-scenario candidate pairs at cosine >=0.85, including one cross-batch requirement pair; inspected labels agree. Shared scenario/template connections yield one 1,500-row origin component. No independent evaluation partitions exist in this corpus under the origin rule.
- **Decision:** preserve all 78 ambiguity rows with null binary labels in the audit mapping; keep related origins together and obtain fresh validation/test origins before freezing splits. Original sources and labels remain unchanged. See `reports/admission_semantic_grouping.md`.

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

## 7 November 2026 — Stage A concept teach-back

- **Objective:** verify the learner can explain the admission MLP, grouped split leakage, and source-scoped forgetting.
- **Observed:** after feedback on an initial attempt, the learner correctly explained all three boundaries in a revised answer. The core concept teach-back passed. The user's unanswered-clarification statement is treated as a proposed behavior, not an implemented flow.
- **Actual hours:** not measured as a student session.
- **Exit:** Session 02 learner parser exercise and Session 03 toy prediction calculation remain unrecorded; full Stage A sign-off remains open. See `docs/Stage_A_Closure.md`.

## 7 November 2026 — Stage B Session 09, first Batch A tranche

- **Objective:** start the first 25-group, 500-candidate admission batch using the frozen v1.1 annotation rules.
- **Input:** `docs/Admission_Annotation_Guide_v1_1.md`; 80-row pilot kept separate.
- **Work:** authored 100 fictional draft candidates across five groups and a label-free review CSV; recorded provisional metadata in `data/manifest.json`.
- **Verification:** required fields, IDs, text uniqueness, group counts, binary draft labels, pilot exact-overlap and a character-similarity screen passed; see `reports/admission_batch_a_draft_01.md`.
- **Actual hours:** not measured as a student annotation session.


## 8 November 2026 — Stage B Session 10, full Batch B review packet

- **Request:** deliver the complete Batch B as one Excel workbook.
- **Prepared:** 500 fictional candidates in 25 scenarios, a two-sheet workbook with all review rows and a guide, separate assistant draft JSONL, and manifest entries. Added personal/restricted/uncertain cases, context-dependent relevance, duplicate facts and unconfirmed claims.
- **Verification:** unique IDs/text, group counts, label vocabularies, rationales, overlap screen, and saved XLSX row/text/blank-field/status/dropdown/filter/pane checks passed; workbook previews inspected. Desktop Excel interaction was not tested. See `reports/admission_batch_b_draft.md`.
- **Boundary:** 1,000 candidates authored; 500 reviewed by the user. Batch B awaits review; uncertain actions have null binary labels, and this packet is not a training input. Batch A/B conservatively share a template family. No split assignment or model training occurred.
- **Actual hours:** not measured as a student annotation session.

## 8 November 2026 — Stage B Session 10, completed Batch B submission

- **Input:** user-supplied `NeuroBrain_Batch_B_Review.xlsx`; original retained and archived byte for byte under data, with a CSV extraction of Review values.
- **Observed:** 500 valid, complete rows with unchanged source text and draft statuses; 319 keep, 153 skip, 28 uncertain. All 1,000 authored Batch A/B candidates now have user submissions.
- **Assessment:** 93 rows differ from assistant drafts. Supported 87 submitted interpretations and recorded six proposed resolutions plus a guideline clarification distinguishing useful open verification questions from verified facts. No proposed changes were applied to the original or frozen guide; see `reports/admission_batch_b_review.md`.
- **Exit:** six label resolutions and the proposed clarification await the user before Batch B closure and Batch C. Remaining uncertain actions must be clarified or explicitly excluded before binary training. Splits remain unassigned and no training occurred.
- **Exit:** Session 09 remains open; 400 drafts and human review remain. The user's separate Python parser and toy-prediction exercises remain unrecorded.
- **Review follow-up:** user supplied all 100 first-tranche rows with valid labels and rationales. Action/type/scope/source matched the drafts on all rows; sensitivity differed on `batch-a-04-10` and is pending adjudication. See `reports/admission_batch_a_review_01.md`. Session 09 remains open.
- **Second tranche:** authored another 100 fictional draft candidates across five groups, generated a blank review CSV, and audited schema, IDs, exact overlap and near-duplicate wording. Two stock phrases were revised. Batch A now has 200 drafts across ten groups; see `reports/admission_batch_a_draft_02.md`.
- **First-tranche adjudication:** user explicitly selected `ordinary` for `batch-a-04-10`. Saved `data/admission_batch_a_adjudicated_01.csv`, preserving the submitted review, with all 100 statuses still draft. The second tranche awaits human review; 300 further drafts remain.
- **Third set:** authored 100 more fictional drafts across five scenarios, varied their order, and generated a blank review sheet. Linked all 300 Batch A drafts under one shared template origin to prevent cross-partition leakage later. The manifest hashes were updated; see `reports/admission_batch_a_draft_03.md`.
- **Third-set review:** user supplied all 100 rows with valid labels and rationales. All five label fields matched assistant drafts on every row; ten notes were retained. The submitted review and hash are in `data/manifest.json`; see `reports/admission_batch_a_review_03.md`. The second-set review and 200 additional drafts remain.
- **Fourth set:** authored 100 more fictional drafts across five scenarios, varied row order, and rewrote five stock acknowledgments found by the similarity screen. The draft, blank review sheet, hash and checks are recorded in `reports/admission_batch_a_draft_04.md`. Batch A has 400 drafts; 100 more remain.
- **Second-set review:** user supplied 100 complete rows. One sensitivity label differed on a generic display rule; applied the user's earlier `ordinary` precedent, preserving the submitted sheet. See `reports/admission_batch_a_review_02.md`. The fourth review and final 100 drafts remain open.
- **Fifth set:** authored the final 100 fictional drafts across five scenarios, revised nine similar phrases, and generated a blank review sheet. The draft, manifest hash, and checks are recorded in `reports/admission_batch_a_draft_05.md`. Batch A has 500 assistant drafts across 25 groups; user reviews 04 and 05 remain open. All splits remain unassigned, and this corpus is not training ready.
- **Fifth-set review:** preserved the user's 100-row submission unchanged. All fields are valid; text matches the draft. Type matches the draft on 97/100 rows; the other four label fields match on 100/100. Two submitted requirement labels are supported by the guide. Proposed requirement for `batch-a-23-16` and fact for `batch-a-22-14` await the user's resolution; see `reports/admission_batch_a_review_05.md`. Review 04 remains open; labels remain draft and splits unassigned.
- **Fifth-set adjudication:** user explicitly accepted both proposed type changes. Saved `data/admission_batch_a_adjudicated_05.csv` and its manifest hash, preserving the submitted review. All 100 statuses remain draft. Batch A has 500 authored candidates and 400 covered by user review; review 04 is the remaining review step before Batch A closure and Session 10's Batch B.
- **Fourth-set review and Batch A closure:** preserved all 100 submitted rows; applied the user's prior general large-print precedent to resolve `batch-a-15-07` sensitivity as ordinary in a separate adjudicated file. All 500 candidates now have solo review, with 299 keep and 201 skip. Schema, IDs, reviewed text, rationales, binary labels and manifest checks passed. Recorded five similar wording pairs; all rows share one template family and all resolved sensitivity labels are ordinary. See `reports/admission_batch_a_closure.md`. Session 09's authoring/review milestone is complete; Session 10 Batch B is next. Labels remain draft, splits unassigned, and no training occurred.

## 8 November 2026 — Stage B Session 10, Batch B adjudication accepted

- **Decision:** user explicitly confirmed all six proposed field changes and the clarification about retaining identifiable unconfirmed claims as open verification questions.
- **Saved:** `data/admission_batch_b_adjudicated.csv`, with all 500 statuses draft; guide v1.2, preserving v1.1; updated manifest hash and review status. Original workbooks, extracted submission and proposal snapshot remain unchanged.
- **Counts:** 319 keep, 153 skip, 28 uncertain. Only the six approved label fields changed; unresolved actions were not forced to binary labels.
- **Exit:** Batch B authoring, solo review and adjudication milestone complete. Both batches now cover 1,000 submitted user-reviewed candidates. Next is Session 11 Batch C with explicit chronology, historical updates and distractors. Full-corpus gates, template grouping and uncertain-row clarification/exclusion remain before binary training; no training or split assignment occurred.

## 8 November 2026 — Stage B Session 11, Batch C labels and B clarification list

- **Request:** show all 28 uncertain B actions and provide Batch C labels.
- **Prepared:** 500 C candidates in 25 scenarios with dated historical context and visible draft labels; exact 28-row B uncertainty list with questions and empty response cells; one workbook with both and a guide. Added an explicit C review-decision field because labels are prefilled.
- **Verification:** source vocabularies, counts, IDs, text uniqueness, exact overlap, similarity screen and saved workbook field/date/blank-input/control checks passed; previews inspected. Four similar C pairs are recorded. The canonical B file is unchanged. Desktop Excel interaction was not tested.
- **Exit:** 1,500 candidates authored, 1,000 A/B candidates user-reviewed, C review pending. All 28 B actions remain uncertain. C uses the shared template family and unassigned splits. No training occurred; see `reports/admission_batch_c_draft.md`.

## 8 November 2026 — Stage B Session 11, Batch C review accepted

- **Decision:** user accepted all 500 visible Batch C assistant draft labels; no label changes were requested.
- **Saved:** `data/admission_batch_c_review_completed.csv`, preserving the original draft sources and marking every review decision `agree`; all rows remain `draft`.
- **Exit:** 1,500 candidates have user-reviewed coverage. The 50 uncertain action labels, 4 uncertain sensitivities and 28 unresolved Batch B rows remain uncertain. Splits, grouping audit and training-readiness checks remain open; no training occurred. See `reports/admission_batch_c_review.md`.

## 8 November 2026 — Stage B corpus integrity and readiness audit

- **Passed:** 1,500 reviewed IDs are unique and accounted for; no exact normalized candidate-text duplicates were found; all draft splits remain unassigned.
- **Found:** all 1,500 records share `assistant-structured-scenarios-a1`; semantic/connected-origin grouping and held-out split design remain open. The corpus has 918 keep, 504 skip and 78 uncertain actions.
- **Decision:** not training-ready. Exclude uncertain actions from later binary training, keep related groups together, normalize the one older Batch A metadata exception in the next canonical release, then create the versioned split manifest. No model training occurred. See `reports/admission_corpus_audit.md`.

## 8 November 2026 — Batch B individual clarifications started

- **Input:** user's explanation for `batch-b-00-02`, requesting keep after resolving the crossing from previous planning records.
- **Assessment:** supplied context does not identify a crossing or its difficulty. Recorded the response verbatim, mapped the proposed fields, and requested the missing fictional detail in `reports/admission_batch_b_clarification_log.md`. Other candidates were not treated as prior conversation history.
- **Exit:** canonical labels and workbook unchanged; 28 uncertain actions remain. This records annotation feedback, not an implemented retrieval feature.

- **Spanish-session follow-up:** user identified the referent of `batch-b-01-00` as the Spanish sessions. Recorded `keep / unresolved_issue / project / ordinary / fictional_assistant_authored` for the clarified example in the individual clarification log. The needed adjustment remains unspecified; no cancellation or sensitive reason inferred. One clarified usefulness resolution, 27 remaining; the original CSV/workbook snapshots remain unchanged and must not receive these labels without the added context.

- **Easier-version follow-up:** user explicitly selected `skip` for `batch-b-01-03`; recorded that reviewer action in the clarification log, preserving uncertain type/scope and the original snapshots. Two action decisions recorded, 26 pending; no default uncertainty-to-skip rule introduced.

## 8 November 2026 — Batch B uncertainty correction supersedes individual discussion

- **Decision:** user withdrew the individual clarification approach: all 28 rows remain uncertain in action/type/scope, judged independently from their original context. No answers will be invented. The Spanish-session keep and easier-version skip are withdrawn; no clarification responses are populated.
- **Saved:** current labels in `data/admission_batch_b_adjudicated_v1_1.csv`, preserving the previous snapshot. Latest user instruction restores `batch-b-07-01` sensitivity to uncertain, superseding its earlier restricted adjudication; the explicit privacy warning remains and no sensitive reason is inferred. Eight sensitivity labels are uncertain. This specific override does not revise guide v1.2 globally.
- **Exit:** 319 keep, 153 skip, 28 uncertain; all rows draft. The current-decision section of the clarification log supersedes its historical entries. Preserve uncertain examples and explicitly exclude them from a later binary input rather than relabeling them skip. No binary export, split or training run performed; original workbooks unchanged.

## 16 November 2026 — Demo-week Day 1, early hosted preparation, Day 5 documentation

- **Done (branch `demo-week-2026-11`):** forget now includes exact-content copies, sibling screen captures and linked cross-route copies; screen-ocr captures are separate sources; the chat guard refuses fewer ordinary questions (it still misjudges some); short unresolved-reference quotes and acknowledgments are dropped at extraction; hosted SQL search/forget parity and a `--hosted` answer bridge were written; the SQL ran on a local PostgreSQL 18, the bridge was tested with mocks only. 82 tests pass.
- **Evidence:** `reports/demo_week/2026-11-17.md` (real local Qwen, F01-F11 with Notion/OCR simulated) and `reports/demo_week/2026-11-16-hosted-prep.md`.
- **Not done:** live Notion, screen capture, Open WebUI and any hosted Supabase run; they need the user's tokens, permissions and accounts.
- **Decisions:** the admission MLP is preview-only and never gates saving; Qwen is the pretrained model, no adapter in the demo; no local cache for hosted answers, because it could serve forgotten notes.
