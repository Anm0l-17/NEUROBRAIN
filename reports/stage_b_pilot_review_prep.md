# Stage B pilot review preparation — 3 November 2026

**Scope:** Sessions 07–08 preparation. This is a machine audit and review handoff, not human label adjudication or a completed Stage B gate.

The existing `data/admission_pilot_v0.jsonl` contains 80 fictional assistant-authored candidates in 16 scenario groups and 16 template families. It has 48 draft positive and 32 draft negative labels. Its current pipeline split is 50 train, 15 validation, and 15 test. Every candidate has nonempty context and a rationale, but all 80 annotation statuses remain `assistant_draft_pending_human_review`.

The existing training loader accepts this dataset only with its explicit draft-pilot override. A direct audit found no scenario or template family spanning splits, no exact duplicate candidate, and no candidate pair with normalized character similarity at or above 0.75 using `difflib.SequenceMatcher`. That similarity check is only a screening aid; a human still needs to check semantic paraphrases and shared origins. The pilot includes easy lexical cues: all six candidates containing the word “still” are labeled positive, as are all three containing “changed.” This is a prompt for review, not evidence that those labels are wrong.

The blind sheet `data/admission_pilot_v0_blind_review.csv` contains the 80 IDs, contexts and candidates, with empty review fields. It omits draft labels, rationales and split names. Follow `docs/Admission_Annotation_Guide.md`, then count agreements, disagreements, ambiguous exclusions and possible duplicates. The original test records were already inspected during the October training pilot, so those results cannot serve as untouched held-out evidence for a revised model.

**3 November update:** A separate provisional five-field draft-label table now records `action`, `type`, `scope`, `sensitivity`, and `source` for every row, each with `status=draft`. The blind sheet has corresponding empty columns. Two independent human reviews and the agreement calculation remain pending; no v1 guide has been frozen. `scripts/score_pilot_reviews.py` is ready to calculate keep/skip Cohen's kappa and type/scope agreement when both completed sheets exist.

**Pilot input SHA-256:** `f276358074504f4ca76167d34c5162e597b42c83f294384a104894c995e5fa2a`.

**Exit:** Session 07's draft pilot and guide are prepared. Session 08's blind human review remains open. Stage A learner teach-back also remains open; no label has been promoted to human-reviewed, and the planned 500-record batch has not begun.
