# Admission pilot v0 — fictional fixtures

## Current reviewed snapshot and next review

**Current version: v0.2.** `admission_reviewed_v0_2.jsonl` contains all 1,584
reviewed records: 960 keep, 528 skip and 96 uncertain (null binary labels).
Fresh tranche 02's four corrections are accepted and recorded in
`admission_eval_fresh_02_adjudicated.csv`. All splits remain unassigned and
annotation status remains draft for the release gate. See
`../reports/admission_reviewed_v0_2.md`. The notes below preserve earlier review
and snapshot history.

**Tranche 02 review received:** all 60 rows are preserved in
`admission_eval_fresh_02_review_completed.csv`. Human review coverage is now
1,584. Four scope/sensitivity proposals await resolution; see
`../reports/admission_eval_fresh_02_review.md`. The v0.1 snapshot below remains
the historical 1,524-row release candidate; the next version will include
tranche 02 after its resolutions are recorded.

`admission_reviewed_v0_1.jsonl` consolidates 1,524 reviewed records with accepted
corrections and review notes. Counts: 930 keep, 510 skip, 84 uncertain. The
uncertain actions have null binary labels; uncertainty states are independent
for every label field. All splits and release status remain pending. See
`../reports/admission_reviewed_v0_1.md` and its JSON hash/count report.

The next review sheet is `admission_eval_fresh_02_review.csv`: 60 new candidates
in six situations. Fill D:H labels, I rationale, J optional notes and K
`reviewed`; preserve the completed copy separately. Its overlap checks and
origin limits are in `../reports/admission_eval_fresh_02.md`. Total authored:
1,584; user-reviewed coverage: 1,524. These 60 unreviewed rows are excluded from
the consolidated snapshot.

## Fresh evaluation candidates — solo review and adjudication complete

**Review received:** all 24 submitted rows are preserved in
`admission_eval_fresh_01_review_completed.csv`. Counts: 12 keep, 6 skip,
6 uncertain. All three sensitivity proposals were accepted; use
`admission_eval_fresh_01_adjudicated.csv` for current labels. It retains draft
status and the six uncertain actions. Sensitivities are 20 ordinary, 2 personal,
1 restricted and 1 uncertain; see
`../reports/admission_eval_fresh_01_review.md`. Human review coverage is now
1,524; source independence and evaluation roles remain unverified. The original
preparation instructions below describe the preserved blank template.

`admission_eval_fresh_01_review.csv` is a blank solo-review sheet for 24 new
candidates across six source situations. Fill label columns D:H, rationale I,
optional notes J and `reviewed` in K. Preserve your completed copy separately.
See `../reports/admission_eval_fresh_01.md` for checks and provenance limits.
These candidates are unassigned and their source independence is unverified.
They are not yet accepted validation/test data. Total authored: 1,524;
user-reviewed coverage: 1,524.

80 assistant-authored English examples in 16 independently authored scenario families.
Every example is fictional, and every label is a **draft pending human review**.
No personal notes, application memory, Kaggle data, or benchmark gold answers were used.
The author's provisional `action`/`type`/`scope`/`sensitivity`/`source` labels
are in `admission_pilot_v0_draft_labels.csv`, all marked `draft`. For a new
review, use a copy of `admission_pilot_v0_blind_review.csv` and
`../docs/Admission_Annotation_Guide.md`; keep the draft-label table hidden
until the review is complete. Audit findings are in
`../reports/stage_b_pilot_review_prep.md`.

The user's single completed review is `../admission_pilot_v0_blind_review (1).xlsx`.
Its completeness check and draft comparison are in
`../reports/admission_pilot_review_2026-11-06.md`; the guide now describes the
solo-review path. The original pilot JSONL and draft labels remain unchanged.
The accepted resolutions are in `admission_pilot_v1_labels.csv`, with every
row still marked `draft`. The frozen v1 rules are in
`../docs/Admission_Annotation_Guide.md`. A 20-row masked-label repeat sheet is
`admission_pilot_v1_repeat_sample.csv`.
The completed repeat is `admission_pilot_v1_repeat_completed.csv`. Its one
scope difference and the resulting v1.1 label file are documented in
`../reports/admission_pilot_repeat_2026-11-06.md`; use
`../docs/Admission_Annotation_Guide_v1_1.md` for subsequent annotation.

Each family has five chronologically ordered candidates (three positive, two negative).
Row order within each family was deterministically shuffled before assigning timestamps;
label order is not a feature. Context is a short fictional scenario description, not a
full evolving conversation. This is a convenience fixture, not a representative sample.

Split: first ten families train (50 records), next three validation (15), last three
test (15). Families and exact normalized candidate text are disjoint. Context repeats
within its family. Cross-family paraphrase similarity still needs human auditing.
The split differs from the full plan's 70/15/15 group target because this is a small
pipeline trial. All drafting happened together; these are not independently collected
or human-annotated evaluation records.

Positive: a reusable preference, decision, correction, specification, milestone or
specific unresolved problem. Negative: incidental session state, irrelevant observation
or acknowledgment. This initial set is deliberately easy and lacks challenging
ambiguity, realistic redundancy, evolving long histories, privacy-policy cases,
multilingual text and a realistic class distribution. It cannot validate deployment.

Fields follow docs/NeuroBrain_Session_Plan.md section 4. A rationale documents the intended
label but never enters model features. `provenance.kind` is fictional_assistant_authored;
`annotation_status` is assistant_draft_pending_human_review. Training refuses drafts
unless --allow-draft is explicitly supplied. That switch authorizes a pipeline trial,
not a declaration that labels are correct or that automatic exclusion is safe.

Test records have now been inspected for this report. Any tuning based on these
findings requires a new independently reviewed held-out set. Preserve v0 unchanged.

## Stage B Batch A — authoring and solo review complete

Batch A has 500 fictional candidates across 25 scenarios. All five user reviews
are complete and recorded differences resolved. The resolved counts are 299 keep
and 201 skip. See `../reports/admission_batch_a_closure.md` for checks and limits.

Draft inputs are `admission_batch_a_draft_01.jsonl` through
`admission_batch_a_draft_05.jsonl`. Original user submissions are
`admission_batch_a_review_01_completed.csv` through
`admission_batch_a_review_05_completed.csv`; they are preserved unchanged.

Use the reviewed label files below by `example_id`, rather than the original
assistant type fields. All reviewed labels remain draft for the later data gate.

| Set | Reviewed label source |
|---|---|
| 01 | `admission_batch_a_adjudicated_01.csv` |
| 02 | `admission_batch_a_adjudicated_02.csv` |
| 03 | `admission_batch_a_review_03_completed.csv` |
| 04 | `admission_batch_a_adjudicated_04.csv` |
| 05 | `admission_batch_a_adjudicated_05.csv` |

Per-set results are in `../reports/admission_batch_a_review_01.md` through
`../reports/admission_batch_a_review_05.md`; `manifest.json` records hashes,
IDs and annotation status. Blank review templates remain available.

All 500 rows share one template origin and have unassigned splits. Keep them
in one partition during the later grouping audit. Five similar wording pairs
are recorded in the closure report. All resolved sensitivity labels are ordinary;
this batch provides no coverage of personal or restricted cases.

Next is Session 10's Batch B: 500 further candidates across 25 new scenarios,
with varied wording, structure and domains. Full-corpus review and the later
split/data gates remain prerequisites for training.

## Stage B Batch B — full review workbook prepared

`admission_batch_b_draft.jsonl` contains 500 fictional assistant drafts across
25 additional scenarios. Review all rows together in
`../outputs/01a19ffe-81a3-7582-918c-3d405c31ec87/NeuroBrain_Batch_B_Review.xlsx`.
The workbook contains blank label/rationale fields and an annotation guide;
assistant suggestions remain outside it. See `../reports/admission_batch_b_draft.md`.

Uncertain draft actions use `label=null`; this review packet is not a binary
training input. Resolve or explicitly exclude unresolved items before preparing
training data. Splits are unassigned and all labels remain draft. Batch B shares
Batch A's conservative template-family grouping pending the later split audit.
Cumulative authorship is 1,000 candidates; all now have submitted user review.

The completed Batch B workbook is archived unchanged as
`admission_batch_b_review_completed.xlsx`; its Review values are extracted to
`admission_batch_b_review_completed.csv`. All 500 rows are complete and valid.
`admission_batch_b_proposed_resolutions.csv` assesses 93 differences from the
assistant draft. The user accepted all six proposed changes and the clarification
on keeping identifiable unconfirmed claims as unresolved verification issues.
Use `admission_batch_b_adjudicated_v1_1.csv` as the current Batch B label source,
with `../docs/Admission_Annotation_Guide_v1_2.md` for subsequent annotation.
See `../reports/admission_batch_b_review.md` for the resolved review. The proposal
CSV remains a historical snapshot. Batch B authoring/review/adjudication is complete;
28 actions remain uncertain and every row retains draft status. Splits are unassigned.
Next is Session 11 Batch C: 500 further candidates with explicit chronological
context, historical updates and distractors.

The user's subsequent correction withdrew the Spanish-session keep and
easier-version skip discussed in chat. All 28 uncertain actions retain uncertain
type and scope. Eight also have uncertain sensitivity, including `batch-b-07-01`
whose earlier restricted label is superseded by this explicit user override.
Its privacy warning still applies. See `../reports/admission_batch_b_clarification_log.md`.
The previous `admission_batch_b_adjudicated.csv`, clarification CSV and workbooks
are preserved historical snapshots; do not invent missing details or apply the
withdrawn decisions. The current version keeps all six other accepted field
resolutions and every row remains draft. No model training or split assignment.

## Stage B Batch C — 500 labels reviewed

`admission_batch_c_draft.jsonl` and `admission_batch_c_draft_labels.csv` contain
500 fictional candidates in 25 dated scenarios under guide v1.2. All draft
labels and rationales are visible as requested. Review them in
`../outputs/01a19ffe-81a3-7582-918c-3d405c31ec87/NeuroBrain_Batch_C_Labels_and_B_Clarifications.xlsx`.
Use column N to record explicit review; a prefilled sheet is not a completed review.

The workbook also contains the exact 28 uncertain Batch B rows, with focused
questions and blank response cells. The source list is
`admission_batch_b_uncertain_clarifications.csv`; this workbook reflects the
earlier B snapshot, before the subsequent sensitivity correction described above.
See `../reports/admission_batch_c_draft.md` for construction, checks and limits.
Cumulative authorship is 1,500; user-reviewed coverage is now 1,500. The
accepted C snapshot is `admission_batch_c_review_completed.csv`; all 500 rows
retain `status=draft` for the later data gate. See
`../reports/admission_batch_c_review.md`. All splits are unassigned and shared
template grouping applies. The 28 unresolved Batch B rows remain unchanged and
excluded from this review.

## Stage B corpus audit — 1,500 records

The current audit is documented in `../reports/admission_corpus_audit.md`.
Integrity checks passed for 1,500 unique reviewed IDs and no exact normalized
candidate-text duplicates. Training is still blocked: all records share one
template family, splits are unassigned, and 78 action labels remain uncertain.

The 9 November semantic screen and origin grouping are complete; see
`../reports/admission_semantic_grouping.md`. Three cross-scenario pairs exceed
the inspection threshold. `../reports/admission_overlap/` records source hashes,
pair evidence and all 1,500 grouping assignments. The 78 uncertain actions
retain null binary labels in that mapping. All records stay in one origin
component with unassigned splits. Fresh validation/test origins are required;
uncertainty is handled through per-head filtering without forced relabeling.
