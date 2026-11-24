# Stage B Session 11 — Batch C visible draft labels and Batch B questions

Prepared on 8 November 2026 at the user's request: all 500 Batch C examples with assistant-proposed labels, plus all 28 accepted Batch B rows whose action is still uncertain. The workbook is `outputs/01a19ffe-81a3-7582-918c-3d405c31ec87/NeuroBrain_Batch_C_Labels_and_B_Clarifications.xlsx`.

## Deliverables and review

- C draft labels: 500 rows across 25 scenarios, with action/type/scope/sensitivity/source, rationale, UTC event time and draft status. The same labeled records are in `data/admission_batch_c_draft.jsonl` and `data/admission_batch_c_draft_labels.csv`.
- B clarifications: the exact 28 IDs selected from `data/admission_batch_b_adjudicated.csv` using action uncertain, with original contexts, candidate texts, accepted labels and rationales. Each has a focused clarification question and an empty response cell. The separate record is `data/admission_batch_b_uncertain_clarifications.csv`.
- Guide: v1.2 rules and instructions for interpreting time, reviewing visible draft labels and adding explicitly fictional follow-ups without guessing missing answers.

Batch C labels are visible because the user explicitly requested labels. They are assistant suggestions, not reviewed ground truth. Mark column N agree/change/uncertain for each row; if changing a label, edit D:I and explain the change in J. A returned prefilled sheet alone does not establish review completion. All statuses remain draft. This workflow cannot measure blind independent reviewer agreement.

For Batch B, column K accepts a clarification response. The cases are fictional: there is no real speaker to interrogate. Any added answer must be explicitly authored as a fictional follow-up and linked to its example ID. Do not invent a reason silently, infer a diagnosis, supply private credentials, or treat a question as answered. Original accepted B labels remain unchanged. Unresolved records can remain uncertain or later be explicitly excluded from binary training.

## Temporal construction

Each scenario has a dated August/September history and an explicit as-of instant of 2026-10-01T12:00:00Z. Candidates are independent snapshots evaluated against that stated history, not sequential conversation turns. Within-scenario order was shuffled with seed 1109 plus scenario index. A proposed correction in one candidate is not automatically added to the context of another candidate.

The scenarios cover current versus obsolete instructions, corrections, future effective dates, exceptions by device/group/edition/item, grandfathered records, old aliases, identity continuity and stale retrieval. Described dates and situations are fictional fixture data, not observed events. Full evolving conversations and diverse as-of dates remain absent.

Draft counts: **300 keep, 150 skip, 50 uncertain**. Sensitivity counts: 431 ordinary, 30 personal, 35 restricted, 4 uncertain. These structured counts do not estimate real-world class prevalence. Uncertain draft actions have null binary labels and require later clarification or explicit exclusion; no binary answer is fabricated.

## Verification and limitations

Verified 500 unique C IDs/texts, 25 groups of 20, valid vocabularies, nonempty rationales, dated context, draft statuses, and no exact normalized overlap with A, B or the pilot. At normalized character similarity 0.78, there are four pairs within C and none against A/B/pilot:

| Pair | Similarity |
|---|---:|
| batch-c-15-05 / batch-c-23-03 | 0.805 |
| batch-c-01-09 / batch-c-21-16 | 0.800 |
| batch-c-15-05 / batch-c-19-13 | 0.800 |
| batch-c-10-16 / batch-c-24-10 | 0.786 |

Character similarity cannot establish semantic independence. C conservatively shares `assistant-structured-scenarios-a1` with A/B because the drafting patterns overlap. All connected rows must remain in one partition in the later audit. These batches alone do not establish independent held-out evaluation evidence.

Saved-file checks verified all 500 C fields and labels against the source, typed UTC timestamps, blank human review decisions, all 28 B rows/questions and blank responses, draft statuses, filters/dropdowns/frozen panes, three visible sheets and no formulas. Workbook previews were inspected, including the timestamp format. Native desktop Excel interaction was not tested. The canonical B file hash is unchanged.

Cumulative authorship is 1,500 candidates across 75 scenarios. User-reviewed coverage remains 1,000 A/B candidates. C authoring is complete; review is pending. The 28 B actions remain uncertain. No split assignment, model training or inference behavior was changed.
