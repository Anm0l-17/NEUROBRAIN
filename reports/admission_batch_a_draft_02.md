# Stage B Session 09 — second Batch A review tranche

**Date:** 7 November 2026. `data/admission_batch_a_draft_02.jsonl` contains 100 fictional assistant drafts across five new 20-record scenario groups: observatory, bicycle-share program, board game studio, ferry cooperative, and print shop. There are 60 draft keep and 40 draft skip labels; every group contains both. Five negative candidates share the topic of nearby unresolved issues without describing the continuing fault. All rows have `split=unassigned` and require human review.

`data/admission_batch_a_review_02.csv` is the label-free review sheet. `data/manifest.json` records the draft hash, IDs, grouping rule, and status. Checks found 100 unique IDs and normalized texts, required schema fields, nonempty rationales, no exact candidate overlap with the pilot or first tranche, and no within-tranche normalized character-similarity pairs ≥0.75. Two stock negative phrases initially triggered the similarity screen and were rewritten before the sheet was finalized. Semantic paraphrase and label quality still need human review.

Batch A now has 200 assistant draft candidates across ten groups; 300 drafts and the human review of this second tranche remain before Session 09's target is complete. The first tranche's one sensitivity difference was resolved as `ordinary` and recorded separately.
