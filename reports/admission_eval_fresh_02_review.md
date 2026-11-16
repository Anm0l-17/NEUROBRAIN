# Fresh evaluation tranche 02 — solo review received

All 60 submitted records are preserved in
`data/admission_eval_fresh_02_review_completed.csv`. Every cell matches the
pasted submission; only a terminal newline was added. Drafts and the blank
review template remain unchanged. No missing referents were supplied.

## Verification and comparison

- Exactly 60 unique submitted IDs cover the source draft; context and candidate
  text match on every row. Label vocabularies, rationales and `reviewed`
  decisions are valid throughout.
- Submitted actions: 30 keep, 18 skip, 12 uncertain. No action differs from
  the assistant draft. Thirteen rows differ on at least one other label field.
- Sensitivities: 57 ordinary, 1 personal, 1 restricted, 1 uncertain.
- Source SHA-256: `518326b862c3a163fbbf3904d0377fd03b9f9a601520384557d8b55ecfb4e41c`.
- Saved submission SHA-256: `77b04b71c6e0aca7ff6aad12142344ec629e85d5e8f5519b47db29529264a03b`.

Retain the submitted `fact` for the unaccepted wooden-counter option: the
candidate states a status, without explicitly asking a question. Retain
`requirement` for unit verification: it directs a check before form entry.
Retain the submitted conservative scope uncertainty on seven deictic rows.
None must acquire a usefulness label or resolved referent from another row.

This comparison describes one person's review against assistant suggestions;
it is not independent inter-rater reliability or model performance.

## Four accepted corrections

The user accepted all four corrections. Current labels are saved separately in
`data/admission_eval_fresh_02_adjudicated.csv`, with draft status and explicit
adjudication notes. Only the four listed label fields changed. The original
submission and proposal CSV remain historical snapshots.

| ID suffix | Field | Submitted | Proposed | Reason |
|---|---|---|---|---|
| 00-07 | scope | session | person | The recurring snack habit remains personal even though it is irrelevant to the printing task. |
| 02-07 | scope | session | person | The reading preference describes a recurring personal taste; action stays skip. |
| 04-07 | scope | session | person | A favourite bus seat is a personal preference; irrelevance does not turn it into a temporary state. |
| 04-09 | sensitivity | uncertain | restricted | The explicit privacy request applies without needing a named referent or sensitive explanation. |

These follow guide v1.2's separation of usefulness, scope and sensitivity, plus
the accepted fresh-tranche-01 privacy precedent. Approval or explicit overrides
were explicitly accepted. Final sensitivity totals are 57 ordinary, 1 personal
and 2 restricted. Scope totals are 30 project, 15 session, 3 person and 12
uncertain. All actions remain as submitted.

## Release and collection status

Human review coverage is now 1,584 authored records. With the four proposals
accepted, cumulative action totals stay 960 keep, 528 skip and 96 uncertain.
Uncertain actions remain dataset members with null binary labels in the next
assembled snapshot. That snapshot must follow resolution, rather than silently
overwriting the existing 1,524-row `admission_reviewed_v0_1.jsonl`.

The tranche retains one provisional origin family and unassigned splits. Its
ten-row scenario structure deliberately repeats five keep, three skip and two
uncertain authoring slots. Row IDs/order, labels, rationales and notes cannot
enter prediction features; repeated sentence and class cues also limit the
evaluation claim even if row order is hidden. Future authoring needs more
natural counts, harder counterexamples and varied context lengths, rather than
repeating this block to reach the remaining 416-record count target.

The separate v0.2 snapshot now includes these 60 rows. Next is continued
collection with those structural limitations addressed.
Template-origin assessment, frozen group splits and final held-out provenance
remain open; no training or confidence measurements have been performed.
