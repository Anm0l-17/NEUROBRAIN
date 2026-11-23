# Stage B Session 09 — Batch A review tranche

**Date:** 7 November 2026. This is the first 100 assistant-authored fictional candidates of Session 09's 500-record target, across five new 20-record scenario groups: food co-op, oral-history archive, water survey, ceramics studio, and language-exchange club. Labels and rationales are drafts for human review. `split` is `unassigned`; these records are not training data or held-out evaluation data.

The draft has 59 keep and 41 skip labels. Each group contains both labels. Five negative candidates use the vocabulary of nearby unresolved issues to test whether the label depends on the actual claim rather than a keyword. The blind sheet is `data/admission_batch_a_review_01.csv`; it omits the draft labels and rationales. The dataset and its SHA-256, IDs, grouping rule, and review state are recorded in `data/manifest.json`.

Checks: 100 unique IDs and normalized candidate texts; required fields and nonempty contexts/rationales; valid binary draft labels; five groups of 20; no exact candidate overlap with the 80-row pilot; no within-tranche pairs at character similarity ≥0.75 under `difflib.SequenceMatcher`. That similarity screen does not rule out semantic paraphrases. All examples and rights remain subject to human review.

**Session 09 is open:** 400 more candidate drafts and human review remain. No split has been frozen and no model training was run.
