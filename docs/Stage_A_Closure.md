# Stage A: foundations and feasibility

**Review date:** 3 November 2026  
**Source of truth:** [NeuroBrain_Session_Plan.md](NeuroBrain_Session_Plan.md), Stage A sessions 01–06.  
**Purpose:** record the artifacts and evidence gathered for Stage A. This checklist does not claim the learner has personally completed the study or explanation tasks.

## Session status

| Session | Deliverable and evidence | Status |
|---|---|---|
| 01 — charter | Scope, user, boundaries, trained/frozen components, and deletion limits are stated in [System_Design_v0.1.md](System_Design_v0.1.md), section 1. | Artifact complete; user teach-back pending |
| 02 — Python foundations | Existing application and lifecycle tests cover file parsing and controlled failures; no isolated learning exercise/notes have been recorded. | Partially evidenced; learner practice pending |
| 03 — ML foundations | This document includes a shape walkthrough below; no learner calculation or teach-back is recorded. | Study/teach-back pending |
| 04 — tiny classifier | [stage_a_toy_classifier.py](../scripts/stage_a_toy_classifier.py) trains a one-feature logistic classifier on four synthetic examples, checks finite gradients, and asserts loss falls and class ordering is correct. | Complete; run evidence below |
| 05 — hardware and model feasibility | Hardware, installed runtimes, local model availability, and a short encoder/generator trial are recorded below. | Technical measurement complete; longer workload profiling remains a later gate |
| 06 — design freeze | Scope, architecture, data boundary, risk register, acceptance targets, annotation rules and session budget are summarized below. | Freeze v1 recorded; learner review pending |

## Machine and model feasibility snapshot

| Item | Observed value | Method / qualification |
|---|---|---|
| Device | MacBook Pro, Mac15,6; Apple M3 Pro, 11 CPU cores | `system_profiler SPHardwareDataType` |
| Memory | 18 GB unified memory | `system_profiler`; hardware-reported total, not free memory |
| OS / architecture | macOS 26.5.2, arm64 | Python `platform.platform()` |
| Python | 3.13.1 | Project `.venv` |
| SQLite | 3.45.3 with FTS5 in the existing verification record | `reports/verification.md` |
| PyTorch | 2.15.0; MPS and CUDA unavailable in this runtime | CPU trial; no GPU acceleration assumed |
| MiniLM | `sentence-transformers/all-MiniLM-L6-v2`, pinned revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; 384 dimensions | Cached and loaded offline. One observed cold model load: 0.143 s; two-text encode: 0.125 s; process peak RSS 0.454 GiB. Tiny sample only, not a throughput benchmark. |
| Generator | `qwen3.5:4b`, Ollama local tag, listed as 4.0 GB | One short local generation returned text but failed the exact “READY” instruction. Runtime is usable; prompt compliance and latency were not assessed. Treat as candidate, not selected/validated generator. |
| Disk | 128 GiB available on the data volume at measurement time | `df -h .`; transient and changes over time |

**Decision:** use CPU-compatible PyTorch for the admission pilot and keep generation optional. The MiniLM encoder is feasible for small local experiments. Do not set a final generator latency or RAM budget from the one-prompt trial; measure a defined prompt/output workload during later evaluation. The currently installed Qwen model can be used for a controlled comparison, with retrieval-only behavior retained as the fallback.

## Session 04 run record

Command: `PYTHONPATH=src .venv/bin/python scripts/stage_a_toy_classifier.py`  
Synthetic data only; no project notes used. The run reported four examples, finite gradients, loss reduction, and correct low/high score ordering. This demonstrates that the installed CPU PyTorch can train a tiny classifier; it says nothing about the admission model's usefulness or accuracy.

## Session 03 shape walkthrough

The toy input batch has shape **(4, 1)**: four examples, one numeric feature each. `Linear(1, 1)` returns four logits, shape **(4, 1)**. `BCEWithLogitsLoss` compares these logits with four binary targets of shape **(4, 1)**. Backpropagation computes gradients for the weight and bias; SGD updates them. The train/validation/test split is not meaningful for four teaching examples. In the real project, related scenarios must be grouped into separate partitions; test labels are reserved until model and threshold selection are frozen.

## Design freeze v1

### Charter and boundaries

- User: one person recalling information from notes they explicitly select.
- Core use: import TXT/Markdown, retrieve evidence with source references, inspect history, and deliberately forget a source.
- Neural contribution: train a small admission MLP on fictional reviewed examples. MiniLM and any answer generator remain pretrained and frozen.
- Privacy policy precedes the model: excluded/secret/unsupported content is rejected regardless of model score. Private notes are inference inputs only, never training data.
- Deletion: remove the selected source and application-controlled derived artifacts, then verify search exclusion. This is not forensic erasure, semantic deletion of overlapping facts, or neural weight unlearning.
- Initial release keeps lexical retrieval and extractive/abstaining behavior available when optional models are unavailable.

### Architecture and schema

Use the current shared Python service layer and SQLite/FTS5 baseline. Keep the semantic encoder frozen. The planned admission model consumes a 384-dimensional text embedding plus four metadata features (388 total), with MLP `388 → 128 → 32 → 1`, ReLU hidden activations and dropout. Only the MLP weights are trained. Store evidence and provenance; every derived artifact must identify its source dependencies so deletion can invalidate it.

### Session budget

The core roadmap is 60 sessions × 2 focused hours = 120 hours, with 24 contingency hours; screen work is a separate 12 sessions. This is a planning estimate, not measured elapsed work. A session is complete only when its listed evidence and exit condition exist.

### Risk register

| Risk | Control / gate |
|---|---|
| Synthetic labels encode author shortcuts | Human review, varied templates, grouped splits, rule/logistic baselines, error analysis |
| Useful memory is wrongly rejected | Target validation recall ≥0.95; suggestion mode unless downstream quality and storage gates pass |
| Leakage inflates results | Group by scenario/template family; reserve held-out IDs before tuning |
| Private content enters training | Policy before model; fictional/reusable training data only; provenance validation |
| Deletion misses derived state | Provenance/dependency inventory, cache invalidation, restart and residual-canary checks |
| Local model overloads memory or stalls UI | CPU-first bounded experiments, measure peak RAM and latency; retrieval-only fallback |
| Results are overstated from tiny samples | Report counts and confidence/limitations; no improvement claim from pilot-sized evaluation |

### Frozen acceptance targets

Targets remain those in [NeuroBrain_Session_Plan.md](NeuroBrain_Session_Plan.md), section 3: admission recall ≥0.95; automatic omission additionally needs ≥10% index reduction and ≤3 percentage-point downstream QA drop; custom QA evidence Recall@5 ≥0.85, correctness ≥0.80, citation support ≥0.95, unsupported abstention ≥0.90; deletion canaries absent on the predefined suite after restart; unaffected-answer drop ≤5 percentage points; retrieval p95 <1 second at 10k chunks. The generator budget remains unset until a representative workload is measured. These are targets, not achieved results.

### Annotation specification

Label usefulness for future task recall, not safety or permission. Positive examples include durable decisions, reusable preferences, milestones, unresolved issues, and corrections likely to matter later. Negative examples include transient chatter, redundancy, irrelevant boilerplate, and temporary status with no future task value. Ambiguous examples go to adjudication or are excluded and counted. Each row records candidate/context, time, integer label, rationale, scenario/template group, annotation status, provenance and split. Train/validation/test partitions group related sources and templates; no private note text is allowed.

## Exit decision

The technical artifacts for Sessions 01, 04, 05, and 06 are recorded. Session 02 has application evidence but lacks a learner exercise record. Session 03's explanation is provided for review, but the learner teach-back is unobserved. Therefore Stage A is **technically prepared, learner sign-off pending**. Before Stage B annotation begins, the user should be able to explain in their own words what the MLP learns, how grouping prevents leakage, and what deletion does and does not remove.
