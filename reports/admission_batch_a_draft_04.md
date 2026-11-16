# Stage B Session 09 — fourth Batch A review set

**Date:** 7 November 2026. `data/admission_batch_a_draft_04.jsonl` contains 100 fictional assistant drafts in five 20-record scenarios: junior chess tournament, garment-repair cooperative, sculpture park, school science fair, and orchard cooperative. There are 60 draft keep and 40 draft skip labels, with both classes in every scenario. `split=unassigned`; all rows need human review. `data/admission_batch_a_review_04.csv` hides draft labels and rationales.

Checks: required fields and rationales present; 100 unique IDs and texts; five groups of 20; no exact candidate overlap with the earlier Batch A sets. A normalized character-similarity screen at ≥0.78 found five stock acknowledgments across groups; they were rewritten before the review sheet was finalized. The final screen found no pairs at that threshold. This does not rule out semantic paraphrases or drafting shortcuts. `data/manifest.json` stores the final hash, IDs and shared template origin.

Batch A now has 400 draft candidates across 20 scenarios. The second and fourth review sheets await human labels, and 100 more drafts remain for Session 09's target. All Batch A drafts share a template origin and must stay in one partition during the later split audit.
