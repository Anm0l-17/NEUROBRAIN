# Stage B Session 09 — third Batch A review set

**Date:** 7 November 2026. `data/admission_batch_a_draft_03.jsonl` has 100 fictional assistant drafts across five new 20-record scenarios: mobile library, solar cooperative, film subtitles, community kitchen, and fabrication lab. It has 60 draft keep and 40 draft skip labels, with both classes in each scenario. Candidate order varies across groups. All splits are `unassigned`, and `data/admission_batch_a_review_03.csv` hides the draft labels for human review.

Checks found 100 unique IDs and normalized candidate texts, required fields, nonempty rationales, five groups of 20, no exact text overlap with the pilot or earlier Batch A drafts, and no within-set character-similarity pairs ≥0.75. The manifest hash and IDs match the final JSONL and review sheet. The similarity check cannot rule out semantic paraphrases or annotation shortcuts.

**Grouping correction:** all 300 Batch A drafts so far reuse a structured drafting pattern. Their `template_family` is now the shared `assistant-structured-scenarios-a1`, so a future train/validation/test split must keep these drafts in one partition. The original distinct scenario IDs remain. The first review's candidate text and IDs were not changed by this metadata correction.

Batch A now has 300 drafts across 15 scenarios. The second and third review sheets await human labels; 200 more drafts remain before Session 09's 500-record target.
