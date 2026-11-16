# Consolidated reviewed snapshot v0.2

`data/admission_reviewed_v0_2.jsonl` includes all 1,584 reviewed/adjudicated
records. It extends v0.1 with 60 fresh-tranche-02 records and the four explicitly
accepted scope/sensitivity corrections. The original submission, proposal CSV,
and historical v0.1 snapshot remain preserved. All records retain draft release
status and unassigned splits.

Actions: 960 keep, 528 skip, 96 uncertain. The 96 uncertain rows have null binary
labels; no uncertain action was converted to keep or skip.

| Field | Known | Unresolved |
|---|---:|---:|
| action | 1,488 | 96 |
| type | 1,489 | 95 |
| scope | 1,489 | 95 |
| sensitivity | 1,571 | 13 |

Review notes, rationales, adjudication notes, original authorship provenance and
per-field label states remain in the assembled records. These annotations must
not be used as prediction features. Source hashes and counts are recorded in
`reports/admission_reviewed_v0_2.json`; the main data manifest points to this
version. Rebuild using
`PYTHONPATH=src:. .venv/bin/python -m scripts.assemble_admission_reviewed`.

Documented family links produce components of 1,500, 24 and 60 records. The
latter two are provisional authoring families, not demonstrated independent
evaluation partitions. Three component IDs alone do not establish a defensible
three-way split. The recurring sentence/class structure in tranche 02 remains
a collection limitation. Another 416 examples would meet the numerical 2,000
target, but collection must address those limitations rather than repeat the
same fixed pattern. Origin assessment, frozen grouped splits, ambiguity
confidence/abstention measurements and the Stage B release checklist remain
open. No model training occurred.
