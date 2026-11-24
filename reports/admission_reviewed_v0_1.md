# Consolidated reviewed snapshot v0.1

Historical snapshot: the current assembler now writes v0.2, including fresh
tranche 02. The v0.1 data and JSON report remain preserved; the rebuild command
below describes the original v0.1 assembly step.

`data/admission_reviewed_v0_1.jsonl` assembles all 1,524 reviewed records from
canonical A/B/C sources and adjudicated fresh tranche 01. Original source files
are preserved. `reports/admission_reviewed_v0_1.json` records source hashes,
the assembled hash, label counts and open gates. Rebuild with
`PYTHONPATH=src:. .venv/bin/python -m scripts.assemble_admission_reviewed`.

| Field | Known labels | Unresolved |
|---|---:|---:|
| action | 1,440 | 84 |
| type | 1,441 | 83 |
| scope | 1,441 | 83 |
| sensitivity | 1,511 | 13 |

Actions total 930 keep, 510 skip and 84 uncertain. All uncertain action labels
are null in the binary field and remain available as ambiguity probes. Each
field has its own reviewed/unresolved state. Authorship provenance remains
fictional assistant-authored; label provenance separately records solo human
review. Review rationales, notes and adjudication notes are retained, including
the Batch B privacy override and the fresh tranche's candidate-support caveats.

The older 100-row Batch A review lacking a status field is normalized in this
new snapshot. Every assembled record has annotation status
`single_human_reviewed_draft`, `split=unassigned` and a nullable `parent_id`.
This marks reviewed coverage while retaining the data-release gate. It does not
grant storage permission. No record is promoted to a training release.

Documented template connections yield components of 1,500 and 24 rows. The
second component's independence remains provisional, and two components cannot
provide the required independent three-way partition. Reviewed notes and gold
labels must stay outside prediction features. No class weights can be fixed
until training IDs exist; any weights must use the filtered training subset.

Checks validate accepted overrides, preservation of notes, per-field states,
ID uniqueness, vocabulary, rationales and null binary labels. Fresh tranche 02
is unreviewed and deliberately absent from this snapshot. Splits, evaluation
origin assessment, abstention evaluation and Stage B release gates remain open.
