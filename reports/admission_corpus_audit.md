# Stage B — 1,500-record corpus audit

**9 November follow-up:** offline semantic screening and origin grouping are
complete; see `admission_semantic_grouping.md`. Three cross-scenario pairs were
flagged. All 1,500 rows remain connected by documented origin, so fresh
evaluation origins are needed. The open-check list below preserves the earlier
audit snapshot.

This audit covers the canonical reviewed label sources for Batches A, B and C
after Batch C review acceptance.

## Passed checks

- 1,500 reviewed rows are present with 1,500 unique IDs: 500 per batch and 25
  scenario groups per batch.
- No exact normalized candidate-text duplicates occur across the corpus.
- The reviewed action totals are 918 keep, 504 skip and 78 uncertain.
- The 78 uncertain actions are the 28 preserved Batch B cases and 50 Batch C
  cases; none were converted to skip.
- Reviewed source IDs map to the 1,500 draft candidates without missing IDs.
- All draft JSONL records use `unassigned` splits and the expected fictional
  assistant-draft provenance.

## Gates still open

- All 1,500 records use the single template family
  `assistant-structured-scenarios-a1`. The 75 scenario groups are not yet
  evidence of independent evaluation partitions.
- Scenario contexts intentionally repeat within groups; exact candidate text
  is unique, but a semantic paraphrase audit and connected-origin grouping
  are still required before splitting.
- The 4 uncertain Batch C sensitivities remain uncertain. Uncertainty does not
  grant storage or sharing permission.
- The canonical A/B/C label artifacts retain draft status by policy. One older
  100-row Batch A completed-review file does not include a `status` column, so
  that historical metadata should be normalized only when the next canonical
  release is assembled; the source file remains unchanged.
- No train/validation/test IDs have been assigned, and no binary training file
  has been exported.

## Decision

The corpus is not training-ready. Keep all related records together during the
semantic/template grouping audit, exclude uncertain action rows from any later
binary input, define a grouped held-out evaluation set, and then produce a
versioned training manifest before running baselines or the admission MLP.

The accepted uncertainty policy is now explicit: retain uncertain rows as an
ambiguity set, filter each prediction head by its own known-label vocabulary,
assert that uncertain rows do not reach a binary loss, and report their
confidence/entropy separately. A later clarification creates a new linked row;
it does not overwrite the original ambiguity example.
