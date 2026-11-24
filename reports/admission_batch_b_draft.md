# Stage B Session 10 — full Batch B review workbook

Prepared on 8 November 2026: 500 fictional assistant-authored candidates across 25 scenarios, delivered together in `outputs/01a19ffe-81a3-7582-918c-3d405c31ec87/NeuroBrain_Batch_B_Review.xlsx`. Draft labels and rationales are stored separately in `data/admission_batch_b_draft.jsonl`; the workbook does not contain an answer sheet or hidden draft labels.

## Review workflow

The Review worksheet has one filterable table containing all 500 rows. The first ten columns preserve the previous CSV review schema. Additional columns hold `status=draft` and the scenario group. Columns D:I accept the five labels and a rationale; J is optional notes. Labels have dropdowns, the header and example ID column are frozen, and context/candidate text wraps. The Guide worksheet explains the allowed values, scope, sensitivity, uncertainty and accepted Batch A distinctions. All review fields begin blank. Source labels must reflect the fictional assistant origin, not the in-scenario speaker.

## Coverage

There are 20 candidates in each scenario: bicycle commuting, language exchange, household move, audio documentary, seed imaging, volunteer shifts, freelance invoices, oral-history catalog, hill walking, accessible seminar, family recipe binder, dissertation references, camera-drone repair, game localization, community food cupboard, ceramics catalog, mentoring calendar, private budget notebook, permission-controlled journal import, museum textile captions, cat-care reminders, recipe booklet production, command-line synchronization, choir transport and pier-photo archive.

Draft action counts: 297 keep, 153 skip, 50 uncertain. Sensitivity counts: 399 ordinary, 40 personal, 53 restricted, 8 uncertain. The candidate set includes useful sensitive details, irrelevant sensitive examples, redundant facts already in the stated context, irrelevant tutorial instructions, explicit adopted decisions, existing routines, and unconfirmed claims. Counts describe assistant suggestions, not reviewed ground truth or the natural distribution of user memories.

Every context and person is invented. Sensitive cases describe constraints or private material without including real credentials or records. A keep label denotes usefulness and never overrides consent or permission. Named scenarios are independent contexts for annotation, not full evolving histories. Within-scenario row order was shuffled using seed 1108 plus scenario index. Event timestamps are synthetic ordering metadata and do not establish an observed chronology.

## Checks and limits

- Verified 500 unique IDs and normalized candidate texts, 25 groups of 20, valid label vocabularies, nonempty draft rationales and both definite action classes in each scenario.
- No exact normalized candidate overlap with Batch A or the pilot. Three phrases detected by a character-similarity screen were rewritten before workbook export; the final screen found no pairs at 0.78 or above within Batch B or against Batch A/pilot. This does not establish semantic independence.
- Verified the saved XLSX contains all 500 source contexts/candidates unchanged, seven blank review columns, 500 draft statuses, two visible sheets, six list-validation ranges, a filterable table, and frozen header/ID panes. No formulas or assistant answer sheets are present.
- Visually checked workbook previews. Native desktop Excel interaction was not tested.

Batch B conservatively shares `assistant-structured-scenarios-a1` with Batch A because the drafting process and several semantic archetypes overlap. A later split must keep related patterns together; a new batch name does not create independent test evidence. All splits remain unassigned and annotations pending human review.

Uncertain draft actions have `label=null`, not a fabricated binary answer. This review packet is intentionally not a `scripts/train_admission.py` input: resolve uncertainty or explicitly exclude unresolved rows before preparing binary training data. The current trainer rejects nonbinary labels. No training code or gates were relaxed.

Cumulative authorship is 1,000 candidates across 50 scenarios. Human-reviewed coverage remains Batch A's 500 candidates. Session 10 review is pending, and all labels remain drafts for the later full-corpus gate. The manifest records draft/workbook hashes and IDs.
