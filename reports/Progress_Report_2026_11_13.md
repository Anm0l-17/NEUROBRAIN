# NeuroBrain progress report — 13 November 2026

This is the current checkpoint after the overnight coding sessions. It supersedes the earlier readiness estimate for current status, while preserving the earlier audit as historical evidence. The presentation target remains 23 November, with rehearsal on 22 November.

## Plain-language report

NeuroBrain now has a working local memory demonstration. It can take selected fictional text, extract supported notes, save them, answer using citations, update the remembered information and forget it while keeping unrelated information. The browser shows where observations came from instead of presenting an internal generated filename as the source.

The main unfinished part is the full real-world connection: selected Notion and VS Code windows, real Supabase storage, and the final Open WebUI experience working together in one supervised session. The database foundation for this is stronger now, but local tests do not prove those account and permission steps.

Estimated readiness for the documented prototype is **65–70%**. This is a delivery estimate, not accuracy or full research-project completion. The previous assessment was about 60%. The improvement comes from successful local end-to-end demonstrations, reviewed lifecycle fixes, browser verification, PostgreSQL validation and presentation preparation. Live acceptance remains mandatory regardless of the percentage.

## Updated stage table

Stages refer to the full Session Plan. Work was brought forward for the prototype; progress in a later stage does not automatically close every earlier research gate.

| Stage | Technical meaning | Plain-language meaning | Completed evidence | Remaining work / status |
|---|---|---|---|---|
| A — Foundations, sessions 01–06 | Scope, learning, hardware feasibility and architecture freeze | Understand what we are building and confirm the laptop can run its parts | Stage A closure records learner sign-off; local encoder and generator feasibility measured | **Foundation milestone complete.** Longer workload profiling belongs to later gates. |
| B — Data, sessions 07–16 | Annotation, provenance, grouping and evaluation corpora | Prepare examples and fair tests | 1,584 reviewed fictional rows; 96 uncertain actions retained with null targets; frozen exploratory grouped split and checks | **Exploratory admission data ready; full stage incomplete.** Original plan includes 2,000 admission examples, 100 dated notes/200 QA items, 40 deletion scenarios and external benchmark preparation. Independent generalization is unproven. |
| C — Memory baseline, sessions 17–24 | SQLite/FTS5, MiniLM retrieval, versions, citations, policy and deletion | Remember selected notes, find evidence and remove it correctly | Local lifecycle tests; deterministic demo; offline semantic/hybrid retrieval; restart, duplicate, version and deletion checks | **Prototype baseline working locally.** Broader acceptance corpus, recovery/restore and scale coverage remain. |
| C2 — Cloud prototype | Drive/Supabase RPC lifecycle and observation provenance | Store and inspect memories in the online database | Drive adapter and SQL; observation schema extension; real disposable PostgreSQL tests for versions, retries, owner isolation and forgetting | **In progress.** Explicit hosted-save code exists, but its Python integration tests/review and complete hosted retrieval interface remain unfinished. No real Supabase rehearsal or deployment. |
| D — Admission model, sessions 25–36 | Frozen encoder + 388→128→32→1 MLP, baselines and validation | Train a small model to estimate whether something is worth remembering | Five baselines; four configurations plus two seed repeats; checkpoint reload; offline preview inference | **Exploratory training done; research gate open.** Final model/policy selection, ablations, formal model report and reserved final evaluation remain. No demonstrated MLP advantage. |
| E — Integration, sessions 37–46 | Extraction, evidence selection, UI, admission controls and lifecycle coordination | Make the parts work as one assistant | Local Qwen extraction; cited memory API; browser lifecycle; chat recovery; current evidence/provenance validation | **Partially integrated.** Admission does not control saving; review/abstention workflow, full cloud-backed chat, temporal reasoning and final Open WebUI acceptance remain. |
| F — Evaluation, sessions 47–54 | Held-out QA, deletion, security, failure, performance and offline evaluation | Prove it works beyond a few examples | 68 current Python tests; real local-model smoke runs; browser checks; PostgreSQL lifecycle tests; lint/format clean | **Development verification working; full research evaluation pending.** No broad accuracy, 10k-chunk performance, network-blocked whole-system proof or completed external benchmarks. |
| G — Delivery, sessions 55–60 | Reproducibility, report, slides, release and rehearsal | Prepare the final presentation package | Audit and progress reports; repeatable demo script; five-minute run sheet; 13 draft supervised fixtures | **Preparation underway.** Finished slide deck, final report/model cards, clean-install release and actual rehearsal/sign-off remain. |
| H — Screen observation | Approved-window ScreenCaptureKit + local Vision OCR | Read a new fact typed on screen before the file is saved | VS Code window helper, identity/focus checks, observer wiring and simulated regression tests | **Implemented, live acceptance pending.** Real unsaved fact, permission revocation, overlays/closed windows, pause/focus switching and cross-route duplicate merging must be demonstrated. |

## What is working, and how strongly it is verified

| Function | Current evidence | Practical boundary |
|---|---|---|
| Local note import, duplicate suppression and persistence | Automated lifecycle suite and deterministic walkthrough | Selected supported TXT/Markdown inputs only |
| Extraction → storage → cited answer → update → forget | Two real local-Qwen walkthroughs, 5.110 and 5.173 seconds total | Tiny fictional warm development runs; an earlier 60-second timeout remains unresolved as a reliability event |
| Correct citation identity | Model output schema restricted to retrieved IDs; application validates again | Correct citation does not prove relevance or usefulness |
| Updating an extraction without changing raw source text | New version replaces current extraction; idempotent repeats tested | Old versions remain inspectable until forgotten |
| Forgetting and retaining unrelated memory | Restart/tombstone tests and local demo; stale HTTP evidence rejected | Original files, backups, prior chat history and already-delivered/network-buffered answers are outside deletion |
| Provenance display | Browser source list, search and inspection checked; semantic provenance regression | Real page/window capture not established by the fictional browser fixture |
| General terminal chat | Routing tests; failed turns preserve prior successful history | Separate from memory; factual mistakes and slow reasoning remain possible |
| Memory HTTP bridge | Authentication, stream framing, deletion and stale-response tests | Open WebUI itself still unverified; referential pronouns are conservatively rejected rather than resolved |
| PostgreSQL storage lifecycle | Real PostgreSQL 17 fixture passed with fictional Auth users | Local database test, not hosted authentication/RLS acceptance on Supabase |
| `--save-hosted` observer option | Implemented with explicit opt-in and acknowledgment check | **Not yet verified end to end; do not describe as working cloud integration** |

## Technical checkpoint

- Current full command: `PYTHONPATH=src:. HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -m unittest discover -s tests -v` — **68 passed**, no skips, with loopback permission.
- Ruff check, Ruff formatting check (40 files) and `git diff --check` passed. Test count is not test coverage or model accuracy. The latest hosted saver needs dedicated tests beyond the existing suite.
- Model-backed demonstration: [demo_observation.py](../scripts/demo_observation.py). Success requires every lifecycle assertion to pass. Recorded runs are [local_demo_01.json](overnight_2026_11_13/local_demo_01.json) and [local_demo_02.json](overnight_2026_11_13/local_demo_02.json).
- SQL evidence: [postgres_c2.txt](overnight_2026_11_13/postgres_c2.txt) and [postgres_observation.txt](overnight_2026_11_13/postgres_observation.txt). Both execute inside a disposable transaction; the observation extension preserves existing Drive calls.
- Admission frozen split: 1,500 training rows (1,422 binary / 78 uncertain), 24 validation rows (18 binary / 6 uncertain), 60 reserved final rows (48 binary / 12 uncertain). Frozen SHA remains `d91b7314d7e751351f0e6f6e58cd64dfafa4913e7e1be3381ec87599b192dab1`.
- Selected exploratory MLP validation average precision ~0.7755 versus embedding logistic ~0.8674, on just 18 known validation examples. Six MLP trials report F1 ~0.8571. This does not establish broad accuracy or improvement.
- Qwen3.5 and MiniLM remain pretrained/frozen. The `neurobrain-test` alias is prompt/runtime customization, not a newly fine-tuned generator. Adaptive routing is in the terminal launcher and is bypassed by direct Ollama/Open WebUI calls.
- Four CodeRabbit code-scoped reviews completed: 7, 7, 3 and 3 issues, with repeats and conditional checks. Valid issues were fixed; unsupported conditions were checked against actual modules/callers. [Dispositions](overnight_2026_11_13/review_disposition.md). The latest hosted changes are newer than those reviews and still need review.
- Existing work was preserved. No commit, push, model retraining or hosted deployment occurred in this overnight work. A disposable local PostgreSQL container is still available for the ongoing integration tests; it must be removed when that work ends.

## Overnight work completed

1. Diagnosed the extraction timeout sufficiently to reproduce a successful fresh-runner request; did not pretend the underlying transient issue was permanently fixed.
2. Built a repeatable model-backed lifecycle demonstration and fixed the citation failure it exposed.
3. Fixed changed-extraction versioning, improved observation provenance across retrieval/UI, handled cloud resets and preserved interactive chat history after failures.
4. Added delivery-time evidence validation coordinated with deletion, with a bounded client/network limitation documented.
5. Fixed source-reference grouping and portable UTF-8 frozen-file writes without changing frozen dataset contents.
6. Ran browser and real PostgreSQL verification and prepared a five-minute run sheet with draft fixtures.
7. Started hosted observation integration: schema/provenance extension, validated saver and explicit observer option. This session remains open.

## Remaining work, in priority order

| Priority | Technical next step | Plain-language result | Needs user access? |
|---|---|---|---|
| 1 | Dedicated tests/review for hosted saving; add hosted search/inspect/preview/forget and align answer backend | Online memories can be saved, found and removed through one coherent workflow | Implementation no; real hosted proof yes |
| 2 | Verify selected Notion page and approved VS Code OCR on the actual Mac | Show a new fact reaching memory from each required app | Yes: selected fictional sources and real permissions |
| 3 | Verify Open WebUI `neurobrain-memory` connection against the same database | Ask questions in the intended interface and see correct citations | Yes: final configured UI acceptance |
| 4 | Define/test uncertainty and saving policy; cross-route deduplication | Avoid saving ambiguous chatter or duplicating the same screen/file fact | Implementation no; fixture/sign-off review yes |
| 5 | Repeat cold/warm, timeout, outage, pause/revocation and change-to-commit tests | Know what happens when the laptop/network/app behaves badly | Some supervised live cases |
| 6 | Finish deck, release evidence and rehearsal | Deliver a clear, repeatable presentation | Final rehearsal/sign-off yes |

Further Qwen training, a new frontend, a third application and broad benchmark expansion are not prerequisites for the current demo. Admission research still needs its final protocol gates before claiming learned automatic selection.

## Readiness estimate, same weights as the original audit

| Component | Weight | Estimated completion now |
|---|---:|---:|
| Design/materials | 10% | 75% |
| Inputs/observation controls | 15% | 65% |
| Extraction/evidence validation | 15% | 75% |
| Local memory/retrieval/forgetting | 15% | 95% |
| Hosted persistence | 15% | 45% |
| Chat/interface | 10% | 75% |
| Privacy/admission/failure behavior | 10% | 70% |
| Integrated acceptance/rehearsal | 10% | 35% |

Weighted estimate: 67.5%, communicated as **65–70%** to avoid false precision. This is not the percentage of full research stages completed. The minimum credible local demo works; the documented two-app, unsaved-screen, hosted presentation is not yet fully ready.

Unverified: live Notion, real screen/permission transitions, hosted Supabase and final Open WebUI acceptance. The remaining risk is integration and reliability, not absence of the local memory foundation.
