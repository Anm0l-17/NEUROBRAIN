# Professor checkpoint: system design and basic module implementation

**Checkpoint:** 27 October 2026. **Requirement:** “Each team is expected to present the system design along with the basic implementation of the proposed modules.”

## What to show

1. **Problem and scope, 30 seconds.** A local assistant needs inspectable memory, evidence-backed recall, and deliberate removal. First inputs are selected notes; automatic screen capture is deferred.
2. **System design, 60 seconds.** Show the implemented architecture and schema from `System_Design_v0.1.md`. Explain the common services behind CLI and web. Show the larger neural architecture separately as the proposed next stages.
3. **Working modules, 2 minutes.** Import the two fictional example notes. Search `SQLite`; inspect its citation and line range. Import the same file again and show that it is already stored. Search an absent term to demonstrate no evidence.
4. **User control, 60 seconds.** Preview forgetting `project.md`, confirm, and search `SQLite` again. Verify that the project original still exists and the `Mira` preference remains searchable. Explain source-scoped application deletion and exact-content reimport blocking.
5. **Evidence and next milestone, 30 seconds.** Show `reports/verification.md`. Explain the planned trained admission head and the dataset required before training. Do not call keyword search a neural model or matching excerpts generated answers.

For a fresh, repeatable eight-step demo with automatic restart checks:

```bash
PYTHONPATH=src python3 scripts/demo.py
```

It uses a temporary database and fictional notes, and cleans up afterwards. Browser demo data is persistent: once forgotten, identical example content stays blocked in that database. Use a new explicit `--db` filename for each fresh presentation rather than removing privacy tombstones from an existing database.

## Relationship to the 60-session plan

The session plan remains the full research schedule. This request authorizes implementation and adds an earlier presentation checkpoint. We brought forward basic deterministic modules to produce something demonstrable; this does **not** imply the dataset or prerequisite stages are complete.

| Session scope | Current evidence | Remaining before calling the session complete |
|---|---|---|
| 01 | Charter and scope in system-design document | Student review and explanation |
| 02 | Real parser, controlled errors, tests | Student practice/learning artifact if needed |
| 03–06 | Architecture and targets remain in session plan | Neural learning exercises, machine/model measurements and design freeze |
| 07–16 | Two fictional demonstration notes only | Label guide, admission pilot, human review, grouped splits, QA/deletion corpora and benchmark manifests |
| 17–20 | Package, schema v1, shared services, policy, note import, FTS, inspection | Ten-note acceptance corpus and expanded policy/lifecycle review |
| 21–22 | Lexical baseline only | Frozen embeddings, cosine search, reciprocal rank fusion and retrieval comparison |
| 23–24 | Transactional source/chunk/FTS deletion; tested rollback/restart/version changes | Extended cases for future vectors/artifacts, restore semantics, full stage-C report |
| 25–36 | Neural architecture documented | Feature pipeline, baselines, MLP, checkpoints, curves, validation/test results |
| 37–46 | Basic web import/search/inspection/deletion brought forward | Admission integration, local generator, temporal facts and broader lifecycle safety |
| 47–60 | Small development regression suite | Frozen held-out evaluation, performance/offline/failure testing, release/report/slides |

## Next work units

1. Review this prototype together, agree the professor's demo date and which proposed modules must appear in that checkpoint. Keep the full plan's quality targets intact unless explicitly revised.
2. Complete the session-05 hardware/encoder/generator trial. Python 3.13.1 and SQLite FTS5 worked for the deterministic baseline; this does not establish PyTorch or model compatibility. Choose the training environment based on that trial.
3. Write the annotation guide and 80-example fictional admission pilot (session 07), then review labels (08). Keep uncertain labels in a review queue. Never use private notes as training data.
4. In parallel as a workstream, expand the ten-note deterministic acceptance corpus and add embedding/hybrid retrieval (21–22). This ordering overlaps work units; it does not waive the dataset gate before neural training.
5. Train and compare rules/logistic/MLP only after leakage-controlled data is ready. Integrate suggestion scores first. Keep screen observation after core lifecycle evaluation.

Do not spend the current checkpoint downloading public benchmarks or building a separate frontend framework before the basic presentation has been reviewed.
