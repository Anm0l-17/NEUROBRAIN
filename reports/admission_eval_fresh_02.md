# Fresh evaluation candidate tranche 02

Prepared 60 fictional independent candidate snapshots across six situations:
printing-order redlines, puppet rehearsal cues, loom setup, route-survey units,
museum accession and translation handoff. This continues the user's selected
assistant-authored fictional route. No private notes or external material were
used. Publication rights remain unassessed.

## Review

Open `data/admission_eval_fresh_02_review.csv`. Columns A:C contain ID, context
and candidate. Complete D:H with action, type, scope, sensitivity and source;
I with rationale, J with optional notes and K with `reviewed`. Save the completed
copy separately. Use `uncertain` when a judgment lacks context. Candidate rows
do not become conversation history for neighbouring rows.

Draft labels and reasons are preserved separately in
`data/admission_eval_fresh_02_draft.jsonl`. Draft totals are 30 keep, 18 skip and
12 uncertain. Structured counts are intentional authoring coverage, not natural
class prevalence. User review is pending. Human reviewers may disagree with
the suggestions, including on type and scope independently of usefulness.

## Checks

Verified 60 unique IDs/candidate texts, six scenario groups, matching review
contexts/texts, blank review fields, allowed vocabularies, unassigned splits and
binary/null consistency. No normalized exact candidate duplicates with the
1,524 reviewed records. The offline MiniLM screen found no cross-scenario pair
above candidate cosine 0.85 or context cosine 0.90, either within the new set
or against those reviewed records. Maximum candidate cosine against reviewed
records was 0.753393. Encoder revision:
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.

The screen excludes the separate 80-row pilot. It cannot rule out paraphrases
below thresholds or establish independence. The same assistant authored all
six scenarios; they conservatively share the provisional family
`assistant-evaluation-source-situations-02-provisional`. This new identifier
records a collection, not demonstrated independence from earlier collections.
No validation/test role is assigned. Review and origin assessment precede a
frozen split. A common author alone does not prove a shared sentence template;
equally, a new topic or low cosine alone does not establish a new one.

The event time records an authoring reference and has no turn-order meaning.
The project now has 1,584 authored candidates, 1,524 with recorded user review;
416 further authored records would reach the original 2,000 target, but target
count cannot replace the grouping and evaluation gates.
