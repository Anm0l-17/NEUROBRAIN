# Stage B Session 10 — full Batch B user review

**Latest correction:** This report preserves the original review and first accepted adjudication below. Current labels are in `data/admission_batch_b_adjudicated_v1_1.csv`; the user's subsequent correction supersedes the chat's Spanish-session keep and easier-version skip, retaining all 28 uncertain actions/types/scopes. Eight sensitivities are uncertain, including an explicit user override of the earlier restricted sensitivity for `batch-b-07-01`; its privacy request still applies. Current totals: 319 keep, 153 skip, 28 uncertain; 412 ordinary, 38 personal, 42 restricted, 8 uncertain. See `reports/admission_batch_b_clarification_log.md`. Original submissions and the earlier adjudicated snapshot are unchanged.

The user supplied `NeuroBrain_Batch_B_Review.xlsx` on 8 November 2026. A byte-for-byte archive is saved at `data/admission_batch_b_review_completed.xlsx`, SHA-256 `cb7b37ff5c5b9297c2760125802143a9631c6a901f80b6043ee73eafddd465b2`. The original and archive were not edited. `data/admission_batch_b_review_completed.csv` extracts the Review worksheet's values without changing labels, context, candidate text, rationales or notes.

## Completeness

All 500 expected IDs are unique and present, with 20 rows in each of 25 scenarios. Every candidate, prior context and scenario group matches the draft. Every row has allowed values for all five label fields, a nonempty rationale and `status=draft`. There are 146 rows with review notes. No missing annotations or changed source text were found.

Submitted counts: **319 keep, 153 skip, 28 uncertain**. Sensitivity counts: 413 ordinary, 37 personal, 42 restricted, 8 uncertain. These are the user's submitted labels, not an adjudicated training corpus.

| Field | Matches assistant draft |
|---|---:|
| action | 478/500 |
| type | 463/500 |
| scope | 451/500 |
| sensitivity | 481/500 |
| source | 500/500 |

There are **93 rows with at least one difference**; 407 match on all five fields. These are descriptive comparisons to assistant suggestions, not independent inter-rater agreement or model accuracy. `data/admission_batch_b_proposed_resolutions.csv` preserves the original assessment of all 93 differences: 87 supported submitted interpretations and six proposed changes. The user explicitly accepted all six changes and the uncertainty clarification. `data/admission_batch_b_adjudicated.csv` records all 500 resulting label rows with draft status; the submitted workbook and extracted CSV remain unchanged.

## Six accepted resolutions

| ID | Candidate | Submitted field | Accepted | Reason |
|---|---|---|---|---|
| batch-b-02-06 | Four people will live in our household after the move. | scope: project | person | Standalone household composition can help across activities. This does not correct a project-specific record. |
| batch-b-07-00 | Credit the interviewee as Neri rather than Nera. | sensitivity: ordinary | personal | Corrects an identifying personal detail about the interviewee represented in the fictional scenario. |
| batch-b-07-01 | This part was supposed to stay private. | sensitivity: uncertain | restricted | The explicit privacy instruction supports a privacy flag even while its referent remains unclear. The action and scope remain uncertain; do not infer a reason for privacy. |
| batch-b-10-19 | My brother Jalen cooks with us every Friday evening. | scope: project | person | A separately stated recurring household routine can help beyond compiling this binder, consistent with guide v1.1. |
| batch-b-17-02 | An empty amount means unknown, while zero means no planned spending. | type: requirement | fact | Describes the existing meaning of data values rather than instructing someone to adopt a new convention. |
| batch-b-18-15 | Each derived excerpt carries the identifier of its imported source. | type: requirement | fact | Describes existing system behavior; a requirement would explicitly direct that behavior. |

Exactly the six listed label fields changed in the separate adjudicated file. Other submitted fields retain their values; each changed row has an adjudication note and an updated rationale. All 500 labels remain drafts.

## Supported improvements and guideline clarification

Several assistant suggestions were too broad or keyed to sensitive vocabulary rather than actual content. The submitted project scopes for event contacts, task-specific responsibilities and learning issues are supported where the context supplies no cross-activity use. Generic sample labels such as private diary, without the private contents, need not have restricted sensitivity. However, being fictional does not itself make a represented personal or restricted detail ordinary: the entire corpus is fictional. The supplied rationales generally make the content distinction correctly.

The 22 action changes from uncertain to keep all retain the claim as an identifiable open question or verification task, with notes such as unconfirmed or do not store as fact. This interpretation can be supported under usefulness labeling, but must not promote a claim to verified truth. The privacy/permission state remains a separate concern. This review does not implement a storage flow for unconfirmed claims.

The user accepted the following clarification, now published in `docs/Admission_Annotation_Guide_v1_2.md`:

> Judge usefulness separately from factual confirmation. An identifiable unconfirmed claim may be kept as an unresolved verification issue when the context and rationale explain its future value. Retain the original attribution and uncertainty; do not store the underlying claim as verified. Use action uncertain when a missing referent or insufficient context prevents judging usefulness. If clarification is unanswered, the question stays unresolved; no training label supplies a default answer. A keep label never overrides storage permission.

This clarification supports the user's 22 keep/unresolved_issue choices without treating the assistant's draft uncertain labels as gold. The frozen v1.1 guide remains preserved; v1.2 supersedes it for subsequent annotation. Four self-reported learning weaknesses also reasonably use unresolved_issue rather than the assistant's generic fact label. The submitted distinction between an irrelevant example fact and an actual project decision is supported. Layout instructions can be preferences where the user reads them as presentation taste rather than a mandatory acceptance condition; `batch-b-21-16` is retained as a supported preference interpretation.

## Status and next step

All **1,000 authored candidates across Batches A and B now have a submitted user review**. Both batches' recorded label differences are resolved. Batch B's authoring, solo review and adjudication milestone is complete. The canonical Batch B label source is `data/admission_batch_b_adjudicated.csv`, interpreted under guide v1.2. Counts remain **319 keep, 153 skip, 28 uncertain**. Resolved sensitivity counts are 412 ordinary, 38 personal, 43 restricted and 7 uncertain. Original submissions, assistant drafts and the proposal snapshot are preserved.

Next is Session 11: Batch C, 500 additional candidates across 25 scenarios, emphasizing explicit chronological context, historical updates and distractors. This would bring authored candidates to 1,500. Continue with guide v1.2; later full-corpus review, grouping and training-readiness gates remain open.

There are still 28 uncertain actions in the submitted Batch B review. They remain unresolved and need clarification or explicit exclusion before binary training; they must not be converted to skip by default. Shared template-family grouping and unassigned splits remain in force. No model training, independent second-human review or native Excel interaction testing was performed.
