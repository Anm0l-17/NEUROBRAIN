# Stage B Session 09 — fourth 100-row human review

**Input:** `data/admission_batch_a_review_04_completed.csv`, supplied by the user as pasted text; SHA-256 `200a5ba9fcb3af51c077b7eb765858d5a8adb564e4cf5bbc783b1dfc4fac9e57`. The submission is preserved byte for byte.

All 100 expected IDs are unique and in order; context and candidate text match the fourth draft. Every row has valid values in the five label fields and a nonempty rationale; nine rows have notes. Action, type, scope and source each match assistant drafts on 100/100 rows; sensitivity matches on 99/100. There are 60 keep and 40 skip labels. These comparisons are descriptive, not independent reviewer agreement or model accuracy.

For `batch-a-15-07`, “Put board numbers in large print on each table,” the submitted sensitivity is `personal`, with a note that no person is named. Applying the user's previously approved general large-print rule gives `ordinary`. `data/admission_batch_a_adjudicated_04.csv` records this resolution and its reason; all 100 statuses remain draft. Action/type/scope remain `keep/preference/project`. The submission's optional alternative reading as a requirement does not request a type change; the selected type describes a presentation style.

Other notes distinguish current counts from permanent facts, future plans from instructions, and corrections from milestones. No further resolution is pending from this review. All five review sets have now been submitted; see `admission_batch_a_closure.md` for the full Batch A checks and remaining data gates.
