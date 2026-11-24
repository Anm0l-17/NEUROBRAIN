# Fresh evaluation tranche 01 — submitted solo review

All 24 rows were submitted by the user. The original submission is preserved in
`data/admission_eval_fresh_01_review_completed.csv`, with the original contexts,
candidate text, labels, rationales, notes and review decisions. This file has
no status column; human review coverage does not promote it to training-ready
data. The blank sheet and assistant drafts remain unchanged.
All submitted cell values are preserved; the saved CSV adds a terminal newline.
The manifest records both the attachment hash and the saved-file hash.

## Validation

- 24 unique IDs exactly cover the draft; contexts and candidates match.
- Every label is in the guide vocabulary; every rationale is nonempty and
  every review decision is `reviewed`.
- Submitted actions: 12 keep, 6 skip, 6 uncertain. Sensitivities: 22 ordinary,
  2 uncertain. Nine rows differ from the assistant suggestions on at least one
  of action, type, scope, sensitivity or source. These comparisons are not
  independent inter-rater agreement or model accuracy.

The user's conservative uncertainty for `eval-fresh-01-02-3` ('the longer one')
is retained. The forty-second interpretation is plausible, but the reviewer
does not accept it as sufficiently established. No missing answer is invented.
The six uncertain actions retain their own state and must receive null binary
labels in a later assembled dataset. Other submitted type and scope choices
are retained; the guide permits scope uncertainty and judging the candidate's
form rather than inheriting a decision solely from context.

## Three sensitivity changes accepted

The user explicitly accepted all three proposals. The canonical label snapshot
is `data/admission_eval_fresh_01_adjudicated.csv`. Only the three sensitivity
fields below changed; original submission fields otherwise remain intact.
Added `status=draft` and adjudication notes document the release gate and the
accepted reasons. The submitted review is preserved separately.

| ID | Submitted | Proposed | Reason under guide v1.2 |
|---|---|---|---|
| eval-fresh-01-01-0 | ordinary | personal | Attributing passages to the narrator's uncle represents a family relationship and speaker role; anonymity does not remove the personal detail. |
| eval-fresh-01-03-1 | ordinary | personal | The customer's exact delivery date and time represent precise personal availability. It remains project scope and does not imply a confirmed booking. |
| eval-fresh-01-05-3 | uncertain | restricted | 'This bit stays between us' explicitly requests privacy. Missing content keeps action/type/scope uncertain, but the privacy request requires no inferred reason. |

The prior Batch B privacy override was specific to that row and did not change
the general guide. These accepted changes follow the general guide and require
no private explanation or invented referents. Resolved sensitivity totals are
20 ordinary, 2 personal, 1 restricted and 1 uncertain. Actions remain 12 keep,
6 skip and 6 uncertain.

## Candidate support caveats

The user's notes correctly flag two limits in the drafted claims:
`eval-fresh-01-00-0` extends 'every switch' to 'only while supplying backup
power'; `eval-fresh-01-04-1` changes future fencing into a present blockage.
Keep their review notes attached to the submitted labels. The keep/fact labels
represent the user's usefulness/type judgments, not proof that these extensions
are supported by the prior context. They must not be presented as verified
claims in application memory. Candidate rewrites, if needed, require new linked
rows and a new review; the existing evaluation rows remain preserved.

## Status

Human review coverage is now 1,524 authored records, with this tranche's
sensitivity adjudication complete. The tranche remains one provisional authoring
family, with no validation/test split assigned and no demonstrated independent
origin. No model training or confidence evaluation occurred. Next is expanding
the reviewed authoring approach while preserving origin links and obtaining a
distinct final evaluation origin. The six uncertain actions remain unresolved.
