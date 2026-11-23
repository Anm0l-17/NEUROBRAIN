# Admission semantic overlap and origin grouping — 9 November 2026

The offline screen is complete for the 1,500 A/B/C candidates using the current
reviewed labels. All 75 scenarios belong to one connected origin component
because they share `assistant-structured-scenarios-a1`. The full reviewed
snapshot adds fresh01 (24 rows) and fresh02 (60 rows), producing three
documented components. Keep the A/B/C component together: it cannot supply
independent train/validation/test partitions under the current origin rule.

## Evidence

`scripts/audit_admission_overlap.py` loads the canonical reviewed A sources,
Batch B v1.1 and accepted C snapshot, verifies ID coverage and any supplied
review text, and overlays labels in memory. There are 918 keep, 504 skip and
78 uncertain actions. Original inputs remain unchanged. All rows are preserved
in the grouping artifact, including null binary labels for the 78.

The pinned offline MiniLM encoder screens candidate text and prior context
separately. Each candidate is an independent snapshot; adjacent rows are not
conversation history. Across different scenarios, candidate cosine >=0.85
flags three pairs; context cosine >=0.90 flags none. No normalized exact
candidate duplicates were found.

| Pair | Candidate cosine | Inspection |
|---|---:|---|
| batch-a-01-06 / batch-a-12-13 | 0.941 | Paraphrases of observing an export progress bar; both skip. |
| batch-b-10-08 / batch-c-24-14 | 0.912 | Related sesame-avoidance meal requirements; both keep. The festival qualification changes the range of meals covered. |
| batch-a-06-11 / batch-a-13-10 | 0.858 | Similar transitions to the next station; both skip. |

The flags show repeated meanings. They require no label changes or deletions.
Documented shared origin determines grouping independently of the cutoff.

## Artifacts and verification

- `reports/admission_overlap/summary.json`: thresholds, encoder revision,
  counts, limitations and SHA-256 hashes of all 14 source assets.
- `reports/admission_overlap/flagged_pairs.csv`: all flagged pairs and texts.
- `reports/admission_overlap/grouping.jsonl`: 1,500 ID-to-component mappings,
  reviewed action labels, null ambiguity labels and unassigned splits. This is
  an audit mapping, not a training input or frozen split manifest.
- `data/admission_reviewed_exploratory_v0_1.jsonl` and
  `reports/admission_grouped_exploratory_v0_1.json`: a frozen exploratory
  mapping of A/B/C=train, fresh01=validation and fresh02=test, preserving all
  1,584 rows and 96 null action labels. It is not an independent-release claim.

Run with `PYTHONPATH=src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python scripts/audit_admission_overlap.py`.
The script asserts corpus counts and null ambiguity labels. A unit test checks
that shared scenarios and template families connect transitively.

## Decision and next data work

Retain A/B/C as the exploratory training pool with 78 ambiguity probes. The
frozen fresh IDs are usable for pilot mechanics, but claims remain exploratory
until independently designed source situations and sentence structures are
reviewed and audited. Changing family names alone would not establish
independence. The remaining count target is a possible place for that work;
count alone establishes neither independence nor sufficient class coverage.
Do not create another same-template batch merely to reach 2,000.

The grouped artifact already applies per-head uncertainty masking metadata and
freezes the exploratory IDs; a later independent release must replace it.
Clarified rows must
stay with their linked parent group. Ambiguity probes used to tune abstention
become development data; reserve fresh ambiguity probes for final evaluation.

## Limits

Cosine cutoffs are inspection heuristics, not calibrated paraphrase tests.
Low similarity cannot prove independent origin; context can change meaning.
MiniLM truncation can omit parts of long contexts. The screen cannot certify
the absence of overlap below its thresholds. Independent held-out material is
still needed. No model training or confidence evaluation was performed.
