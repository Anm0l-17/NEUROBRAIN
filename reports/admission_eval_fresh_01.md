# Fresh evaluation candidate tranche 01 — 9 November 2026

Prepared 24 fictional candidates across six new source situations: incident
record, oral-history interview, lab notebook, booking correspondence, revision
memo and collection inventory. This small first tranche tests the changed
authoring approach before expanding the remaining data work. It is not the
remaining 500-record batch or an accepted held-out evaluation set.

## Human review

Open `data/admission_eval_fresh_01_review.csv`. Columns A:C contain ID, context
and candidate. Fill D:H with action, type, scope, sensitivity and source using
guide v1.2; put your rationale in I, optional notes in J and `reviewed` in K.
Use `uncertain` wherever the context does not support a judgment. Each row is
an independent snapshot. Keep the completed submission as a separate file.
Assistant suggestions are stored separately in
`data/admission_eval_fresh_01_draft.jsonl`; the review CSV has blank label cells.
This is still a solo human review, not independent human inter-rater evidence.

Draft counts are 13 keep, 6 skip and 5 uncertain; they remain unreviewed. The
lab instruction mentioning 'the longer one' is resolvable to forty seconds in
its context. Pronouns alone therefore do not imply abstention. The explicit
privacy request in the inventory case remains restricted despite missing
referents. No prior A/B/C ambiguity example has been clarified or overwritten.

## Verification and provenance

Verified 24 unique IDs/texts, six groups, matching review text, blank review
fields, binary/null consistency and unassigned splits. No normalized exact
candidate overlap with the 1,500 reviewed A/B/C rows. Offline MiniLM at revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41` screened candidates and contexts
separately: no cross-scenario pair within this tranche or against A/B/C reached
candidate cosine 0.85 or context cosine 0.90. Maximum candidate cosine against
A/B/C was 0.730260. Screening does not certify independence or detect every
paraphrase. It does not cover overlap with the separate 80-row pilot.

All six scenarios conservatively share
`assistant-evaluation-source-situations-01-provisional`. The same assistant
authored them after seeing A/B/C; changed structure and low similarity do not
establish independent source origin. They cannot simply be split into six
independent families. They are evaluation candidates pending human review and
origin assessment; no validation/test role or final test IDs are frozen.

The stored event time is an authoring reference, not a sequence of turns.
These are invented fixtures and no private notes were used. Publication rights
remain unassessed. Source hashes:

- Draft JSONL: `e940a79c5dfa7897ec2ea062f851f3a60948bdc0e82f5e6cbaf6770aa89b8ab5`
- Blank review CSV: `0b32ac50815203b3ac87e8baf0d947c26ba2bc6fb744f1ac1e15a2bcfe2963ef`

Next: review this first tranche, assess its origin and wording, then expand
the accepted approach. A distinct final test origin must still be reserved;
simply renaming this family cannot supply it. Total authored candidates are
1,524, with 1,500 covered by the user's earlier reviews.
