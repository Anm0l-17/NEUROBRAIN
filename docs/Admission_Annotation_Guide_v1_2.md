# Admission annotation guide v1.2 — 8 November 2026

**Status:** Supersedes v1.1 for subsequent annotation after the user's explicit acceptance of six Batch B resolutions and the uncertainty clarification. All earlier guide versions, assistant drafts and user submissions are preserved. `data/admission_batch_b_adjudicated.csv` records that accepted snapshot. The latest user correction is recorded separately in `data/admission_batch_b_adjudicated_v1_1.csv`: all 28 actions/types/scopes remain uncertain, and eight sensitivities are uncertain. The user explicitly overrides the earlier restricted sensitivity for `batch-b-07-01`; its explicit privacy request remains applicable. See `reports/admission_batch_b_clarification_log.md`. This override does not change the general rules below. Every row remains `draft`. This guide defines annotation rules and does not implement a storage or clarification flow.


## Label fields

| Field | Allowed values | Meaning |
|---|---|---|
| `action` | `keep`, `skip`, `uncertain` | Would retaining the candidate help a future task? Use `uncertain` when context is insufficient. This is usefulness, not storage permission. |
| `type` | `decision`, `preference`, `requirement`, `milestone`, `correction`, `unresolved_issue`, `fact`, `transient`, `acknowledgment`, `uncertain` | The main reason for the action; choose the most specific applicable type. |
| `scope` | `person`, `project`, `session`, `uncertain` | How broadly the candidate is likely to matter later: across the person's tasks, within this scenario/project, or only in the current session. |
| `sensitivity` | `ordinary`, `personal`, `restricted`, `uncertain` | `personal` identifies a personal preference/detail; `restricted` flags a potentially sensitive need or constraint for separate privacy review. |
| `source` | `fictional_assistant_authored`, `uncertain` | Origin of these pilot fixtures. This is provenance, not a confidence score. |

The v1.1 label table has `status=draft` for every row while the larger data gate is pending. The solo review and accepted resolutions are documented separately. A second human reviewer is optional for this solo project; any later report must disclose that limitation. The original JSONL and its existing binary labels remain an unchanged pipeline fixture.

## Uncertain-label policy

Keep `uncertain` rows in the versioned dataset with their own state; never map
them to `keep` or `skip`. For binary action training, filter explicitly to
`action in {keep, skip}`, assert that no uncertain row reaches the loss, and
recompute class weights after filtering. Filter `type`, `scope` and
`sensitivity` independently because a row may be usable for one head while
uncertain for another.

Exclude uncertain rows from headline precision, recall and F1. Evaluate them as
a separate ambiguity set with confidence/entropy and selective-coverage
reporting. They are probes for abstention, not a third class; route low-
confidence inference to clarification or no storage. Keep each
`scenario_group` in one split. If a row is clarified later, preserve the
original unresolved row and add a new row with `parent_id` and the clarified
context.

## Decision rules v1.2

- Label `keep` for a lasting decision, preference, requirement, milestone, correction, stable fact, or specific unresolved issue that could help a future task. Label `skip` for acknowledgment, incidental observation, redundant repetition, unrelated text, or a temporary state with no likely future use.
- Read both context and candidate. A failure with a reproducible condition is usually an unresolved issue; “build failed” without cause or continuing relevance may be `uncertain`.
- For `type`, use `milestone` for a particular future event or deadline, not a recurring routine. A recurring routine already in effect is usually `fact`; a newly chosen routine is usually `decision`. Use `requirement` for a stated need or instruction, `preference` for a choice of style or taste, and `correction` when an earlier value is explicitly replaced. A named responsibility is a `fact` unless the sentence states the decision to assign it.
- Choose `person` only when the detail could help across distinct projects or activities. Choose `project` for a named task, course, event, manuscript, or instrument, even if the candidate uses “I.” Choose `session` for passing states. If the boundary is unclear, use `uncertain` and explain why.
- For a correction, scope the **record being corrected**. “Replace the old servings estimate” belongs to the meal-planning project even though household size could help elsewhere. A separately stated recurring household routine can have `person` scope.
- Treat `sensitivity` separately from usefulness. `ordinary` can still be about a person, such as a harmless teaching preference or broad running preference. Use `personal` for household composition, a named person's role, a specific learning weakness, or precise recurring availability. Use `restricted` for a possible dietary or accessibility need, without guessing the reason behind it. A `restricted` candidate still needs deterministic privacy review before storage. Never put real passwords, private notes, or benchmark gold answers into this dataset.
- Judge meaning rather than cue words such as “still,” “changed,” “thanks,” or “remember.” Record a possible duplicate or paraphrase in `review_notes` with the other `example_id`.

## Clarifications accepted after Batch B

- Judge usefulness separately from factual confirmation. An identifiable unconfirmed claim may be kept as an `unresolved_issue` when the context and rationale explain its future value as an open verification question. Retain the original attribution and uncertainty; do not store the underlying claim as verified. Use action `uncertain` when a missing referent or insufficient context prevents judging usefulness. If clarification is unanswered, the question stays unresolved; no training label supplies a default answer. A keep label never overrides storage permission.
- A sentence describing existing data meanings or system behavior is normally `fact`. An explicit instruction or acceptance condition directing that behavior is `requirement`. Existing recurring routines remain distinct from newly adopted decisions.
- Standalone household composition and separately stated recurring household routines can have `person` scope because they help across activities. Scope a correction to the record being corrected. Names, family relationships and precise availability do not automatically widen a task-specific contact or role to person scope.
- Correcting a represented interviewee's identifying name involves a `personal` detail. An invented story character's rename is a different case. Fictionality alone does not make represented private information ordinary: all examples in this corpus are fictional.
- An explicit request that a passage stay private supports `restricted` sensitivity even while its referent is unclear. Keep action and scope uncertain where needed; do not infer a reason for privacy. A privacy flag does not supply missing permission.
- A generic sample label or mention of private material without its contents need not inherit restricted sensitivity. Assess what the candidate actually contains; do not label from sensitive vocabulary alone.

Batch B's 28 uncertain actions remain unresolved. Clarify them or explicitly exclude them when preparing binary training data; never turn uncertainty into skip by default. The canonical label file uses action labels, while the original assistant draft retains its historical binary/null suggestions. All labels remain draft until the full-corpus review, grouping and data gates pass.

## Solo pilot review and revision

1. Complete one human review of all 80 rows using the blank template and a brief rationale per row. Record missing context or duplicates in `review_notes`; use `uncertain` rather than forcing a guess. The 6 November workbook completes this step.
2. Compare the human sheet with the assistant drafts to locate rule gaps. This is descriptive draft-versus-human comparison, not agreement between independent human annotators. The assistant previously showed the draft labels in chat, so this pilot cannot establish a blind reliability estimate.
3. The user accepted the 14 proposed resolutions in `reports/admission_pilot_review_2026-11-06.md`. The resulting labels and individual reasons are preserved in `data/admission_pilot_v1_labels.csv`.
4. The user repeated a 20-row masked-label sample. Nineteen rows matched v1 across all fields; `pilot-03-02` had `project` scope again. The corrected label is in `data/admission_pilot_v1_1_labels.csv`; see `reports/admission_pilot_repeat_2026-11-06.md`. This is a solo stability check, not independent inter-rater agreement.
5. Expand with new fictional examples and fresh held-out scenario groups after the Stage A learner teach-back. The existing pilot test rows were previously inspected and are not untouched held-out evidence. Train only after the new corpus has been reviewed and its data gate passes.

If a second independent reviewer becomes available, `scripts/score_pilot_reviews.py` can calculate keep/skip Cohen's kappa and type/scope agreement from two completed CSV copies. It cannot verify that the reviews were independent.

The pilot is intentionally small and easy. Its main output is clearer rules and an adjudication record, not a model score.
