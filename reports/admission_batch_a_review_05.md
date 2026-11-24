# Stage B Session 09 — fifth 100-row human review

**Input:** `data/admission_batch_a_review_05_completed.csv`, supplied by the user as pasted text; SHA-256 `336c91aeedbd04667b39914df4c3034a9beb6c3a0ad2d2d959b89b10bc863f97`. The submitted file is preserved byte for byte.

All 100 expected IDs are unique and in order. Context and candidate text match the fifth draft exactly. Every row has valid values in all five label fields and a nonempty rationale; 15 rows include notes. Action, scope, sensitivity and source each match assistant drafts on 100/100 rows; type matches on 97/100. Keep/skip counts are 60/40. These are descriptive comparisons with assistant drafts, not independent inter-rater agreement or model accuracy.

## Type review

| ID | Candidate | Assistant draft | Submitted | Assessment under guide v1.1 |
|---|---|---|---|---|
| batch-a-21-04 | Pack each scene's props in a separate case. | decision | requirement | Support the submitted `requirement`: this gives a packing instruction; no explicit choice or adoption is stated. |
| batch-a-24-12 | Inspect the shelter roof after winter storms. | decision | requirement | Support the submitted `requirement`: this gives a maintenance instruction triggered by storms. |
| batch-a-23-16 | Test keyboard navigation before visual polish. | decision | preference | User accepted `requirement`: the sentence directs work order without stating a personal taste or an explicit decision. |
| batch-a-22-14 | Friday afternoons are reserved for cleaning. | decision | decision | User accepted `fact`: the sentence reports an existing recurring reservation without explicitly adopting it. Both the assistant draft and submitted label missed this guide distinction. |

Guide v1.1 uses `requirement` for instructions, `preference` for style or taste, and `decision` for a stated choice. An existing recurring routine is normally `fact`. A recurring reservation is not a `milestone`; milestones are particular future events or deadlines. The note on batch-a-22-14 suggesting milestone therefore does not fit the guide.

The other notes describe plausible alternative readings without changing the selected labels. Presentation styles can remain preferences where no obligation is stated. A current application behavior can be a fact even though it may later change. The brief zero reading at startup does not by itself establish the reproducible overnight-power fault described in a separate row; the submitted `skip/transient` label is supported. The frozen guideline and original submission are unchanged. The two explicitly accepted type changes and their rationales are saved separately in `data/admission_batch_a_adjudicated_05.csv`; all 100 rows retain `status=draft`.

## Current status

Batch A has 500 assistant drafts across 25 scenarios. All five user reviews have now been submitted; see `admission_batch_a_closure.md` for the final Batch A checks. Both type resolutions in review 05 have been explicitly accepted and recorded. All labels remain draft and splits unassigned. All Batch A examples share one template family and must remain in one partition during the later split audit. No training was performed.

Next: Session 10 authors Batch B: 500 additional candidates across 25 new scenarios, varying vocabulary and domain. Training follows the later full-corpus review, split audit and Stage B data gate.
