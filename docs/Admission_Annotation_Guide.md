# Admission annotation guide v1 — frozen 6 November 2026

**Status:** Annotation rules frozen after one human review and acceptance of the 14 proposed resolutions. `data/admission_pilot_v1_labels.csv` records those resolved labels with reasons. The labels remain `draft` for training because the earlier assistant labels were shown in chat, a delayed repeat sample is pending, and there is no independent second reviewer. The original workbook, draft labels and pilot JSONL are preserved.

## Label fields

| Field | Allowed values | Meaning |
|---|---|---|
| `action` | `keep`, `skip`, `uncertain` | Would retaining the candidate help a future task? Use `uncertain` when context is insufficient. This is usefulness, not storage permission. |
| `type` | `decision`, `preference`, `requirement`, `milestone`, `correction`, `unresolved_issue`, `fact`, `transient`, `acknowledgment`, `uncertain` | The main reason for the action; choose the most specific applicable type. |
| `scope` | `person`, `project`, `session`, `uncertain` | How broadly the candidate is likely to matter later: across the person's tasks, within this scenario/project, or only in the current session. |
| `sensitivity` | `ordinary`, `personal`, `restricted`, `uncertain` | `personal` identifies a personal preference/detail; `restricted` flags a potentially sensitive need or constraint for separate privacy review. |
| `source` | `fictional_assistant_authored`, `uncertain` | Origin of these pilot fixtures. This is provenance, not a confidence score. |

The accepted v1 label table has `status=draft` for every row while the delayed repeat check and data gate are pending. The solo review and accepted resolutions are documented separately. A second human reviewer is optional for this solo project; any later report must disclose that limitation. The original JSONL and its existing binary labels remain an unchanged pipeline fixture.

## Decision rules v1

- Label `keep` for a lasting decision, preference, requirement, milestone, correction, stable fact, or specific unresolved issue that could help a future task. Label `skip` for acknowledgment, incidental observation, redundant repetition, unrelated text, or a temporary state with no likely future use.
- Read both context and candidate. A failure with a reproducible condition is usually an unresolved issue; “build failed” without cause or continuing relevance may be `uncertain`.
- For `type`, use `milestone` for a particular future event or deadline, not a recurring routine. A recurring routine already in effect is usually `fact`; a newly chosen routine is usually `decision`. Use `requirement` for a stated need or instruction, `preference` for a choice of style or taste, and `correction` when an earlier value is explicitly replaced. A named responsibility is a `fact` unless the sentence states the decision to assign it.
- Choose `person` only when the detail could help across distinct projects or activities. Choose `project` for a named task, course, event, manuscript, or instrument, even if the candidate uses “I.” Choose `session` for passing states. If the boundary is unclear, use `uncertain` and explain why.
- Treat `sensitivity` separately from usefulness. `ordinary` can still be about a person, such as a harmless teaching preference or broad running preference. Use `personal` for household composition, a named person's role, a specific learning weakness, or precise recurring availability. Use `restricted` for a possible dietary or accessibility need, without guessing the reason behind it. A `restricted` candidate still needs deterministic privacy review before storage. Never put real passwords, private notes, or benchmark gold answers into this dataset.
- Judge meaning rather than cue words such as “still,” “changed,” “thanks,” or “remember.” Record a possible duplicate or paraphrase in `review_notes` with the other `example_id`.

## Solo pilot review and revision

1. Complete one human review of all 80 rows using the blank template and a brief rationale per row. Record missing context or duplicates in `review_notes`; use `uncertain` rather than forcing a guess. The 6 November workbook completes this step.
2. Compare the human sheet with the assistant drafts to locate rule gaps. This is descriptive draft-versus-human comparison, not agreement between independent human annotators. The assistant previously showed the draft labels in chat, so this pilot cannot establish a blind reliability estimate.
3. The user accepted the 14 proposed resolutions in `reports/admission_pilot_review_2026-11-06.md`. The resulting labels and individual reasons are in `data/admission_pilot_v1_labels.csv`. Preserve the original files.
4. After a delay, re-label `data/admission_pilot_v1_repeat_sample.csv` without opening the previous labels. It has 20 blank rows selected with seed 17: one from each of 16 scenario groups and four more from the remaining rows. Compare the repeat with v1 and report every change. This is a masked-label stability check, not independent inter-rater agreement. If it exposes a rule gap, revise the guide as v2 before expansion.
5. Expand with new fictional examples and fresh held-out scenario groups only after the repeat check and Stage A learner teach-back. The existing pilot test rows were previously inspected and are not untouched held-out evidence. Train only after the new corpus has been reviewed and its data gate passes.

If a second independent reviewer becomes available, `scripts/score_pilot_reviews.py` can calculate keep/skip Cohen's kappa and type/scope agreement from two completed CSV copies. It cannot verify that the reviews were independent.

The pilot is intentionally small and easy. Its main output is clearer rules and an adjudication record, not a model score.
