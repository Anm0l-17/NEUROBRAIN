# Prototype presentation readiness — 13 November 2026

**Assessment: approximately 60% ready (55–65% engineering estimate) for the documented 23 November mentor prototype.** This measures delivery readiness, not model accuracy, research completion, or a probability of success. Critical live gates remain open regardless of the average.

## Scope and evidence rules

The owning milestone is [Prototype_23_November_Plan.md](../docs/Prototype_23_November_Plan.md), reinforced by the opening of [NeuroBrain_Session_Plan.md](../docs/NeuroBrain_Session_Plan.md). The 11 November update prioritizes selected Notion page / saved file / approved VS Code window → typed evidence → stored notes → cited questions in Open WebUI → hosted persistence. It explicitly removes training as a prerequisite. The remaining privacy, deletion, two-application and hosted rehearsal gates still apply. Presentation is 23 November 2026; rehearsal is 22 November, Asia/Kolkata. There are ten calendar days from this audit date to presentation.

The older [Presentation_Checkpoint.md](../docs/Presentation_Checkpoint.md) describes the smaller October system-design/import/search/forget demonstration. It is useful as a fallback script, but does not replace November acceptance. The Working Plan is background; the Session Plan is the broader research roadmap. No new external professor rubric was supplied or verified.

No applicable AGENTS.md was found in the project or checked parent directories. Initial Git inspection found ten modified tracked files and substantial untracked work. Existing work was preserved; this report is the only intentional addition. No implementation edits, training, deployment, commit or push were performed.

## Weighted checklist

Weights reflect the current mentor demo, including live evidence and rehearsal. Completion estimates credit implemented and tested portions, discount unverified integrations, and are rounded judgments rather than task-count measurements.

| Component | Weight | Estimated completion | Evidence and remaining gate |
|---|---:|---:|---|
| Design, explanation and presentation materials | 10% | 60% | Architecture, scope, Stage A closure and run instructions exist. Older walkthrough is runnable. No current November deck, complete demo fixture table or rehearsal record found. |
| Selected inputs and observation controls | 15% | 65% | File/flat Notion readers, bounded start/pause/resume/stop and VS Code window helper implemented. Mocked routing/focus checks pass. Live Notion and unsaved-window acceptance unverified; cross-route merging absent. |
| Structured extraction and evidence validation | 15% | 60% | Typed exact quotes, offsets, source/route/time metadata, validation before persistence and privacy-before-inference tests. Historical real-Qwen smoke evidence exists. Ambiguity remains unreliable; today's one-sentence extraction timed out. |
| Local persistence, retrieval, versions and forgetting | 15% | 90% | SQLite/FTS lifecycle, citations, current-version search, receipts, tombstones, restart and optional offline hybrid retrieval tested. Eight-step deterministic demo passed today. Full research-scale evaluation remains open. |
| Hosted persistence and observation provenance | 15% | 30% | Drive adapter, Supabase SQL/RLS lifecycle and Python simulated-HTTP tests exist. SQL fixture is documented as previously exercised locally. No hosted rehearsal evidence; observer and answer bridge use SQLite. Hosted schema needs observation/app/window provenance beyond Drive identifiers. |
| Chat and presentation interface | 10% | 65% | Local web UI and authenticated OpenAI-compatible memory bridge exist; HTTP checks pass. Real Open WebUI connection/rendering and saved model preset not verified. General adaptive chat is a separate path without memory access. |
| Privacy, admission and failure behavior | 10% | 60% | Input policy, scope checks, focus recheck, bounded sessions and deletion tests exist. Model scores are preview-only; save-extracted persists Qwen-selected quotes without a keep/skip/abstain gate. Live denied-window, revocation, cloud outage and forbidden-marker checks remain open. |
| Integrated acceptance, timing and rehearsal | 10% | 20% | Component regressions and deterministic fallback pass. No complete two-app → hosted → UI walkthrough, route timing/retry evidence or frozen release rehearsal found; fresh model request failed. |
| **Total** | **100%** | **57.25% weighted; report as approximately 60%** | **Plausible estimate range: 55–65%. Hosted and live capture gates are mandatory.** |

This is prototype readiness only. The complete research/product roadmap additionally needs broader QA/deletion corpora, independent evaluation, downstream admission comparisons, scale/performance work, reproducible release evidence and final reporting. A defensible full-product percentage cannot be inferred from these prototype weights.

## What is actually implemented and checked

### Memory and retrieval

- `src/neurobrain/core.py`: explicit note policy; versioned SQLite sources/chunks; exact spans and citations; current-version FTS search; duplicate suppression; all-version forgetting with receipt and content tombstone; observation metadata.
- `src/neurobrain/semantic.py`: pinned offline MiniLM, semantic index, hybrid retrieval, lexical fallback and deletion invalidation. Current Qwen evidence answers call lexical `store.search`; hybrid is a separate CLI operation.
- `src/neurobrain/cli.py`, `web.py`, `index.html`: basic operator/UI lifecycle. The old policy output still says “no trained model”; this describes its ungated import path, although trained experimental checkpoints now exist elsewhere.
- Today's `scripts/demo.py` passed all eight steps: import, duplicate, privacy rejection, evidence, no-evidence, forget, receipt and restart with unrelated memory retained.

### Observation and extraction

- `observe.py`: separate selected Markdown, flat Notion page and VS Code screen routes; five-minute interactive watcher; optional MLP scores; optional extraction/local save. Saved-file input identifies the route, not which editor wrote the file.
- `screen.py` / `scripts/window_probe.swift`: exact foreground VS Code window checks, ScreenCaptureKit capture, local Vision OCR, identity checks after OCR and before writing. Tests simulate helper output; they do not prove actual OS permission, overlays, focus transitions or revocation behavior.
- `extract.py`: pretrained Qwen3.5 selects typed contiguous quotes; application verifies quotes/spans and rejects malformed or truncated responses. Citation selection returns stored excerpts, not unrestricted generated answers. Note usefulness/type remains a model judgment.
- Historical extraction reports show that ambiguous instructions can be incorrectly retained. Quotation validation does not establish standalone meaning or usefulness. `--save-extracted` is an explicit save request; combining it with `--checkpoint` does not turn scores into a saving policy.
- Exact duplicates on one source route are handled; the same document through screen and saved-file routes has different identities and is not merged. Persisted observation metadata lacks the full planned app/window-session/admission-policy provenance.

### Admission data and trained head

- Verified frozen exploratory bytes: 1,584 fictional reviewed records, SHA-256 `d91b7314d7e751351f0e6f6e58cd64dfafa4913e7e1be3381ec87599b192dab1`.
- Frozen split: training 1,500 rows (918 keep / 504 skip / 78 uncertain), validation 24 (12 / 6 / 6), reserved final test 60 (30 / 18 / 12). All 96 uncertain action labels remain null. Known binary targets are 1,422 train, 18 validation and 48 final test.
- Current selector/history safeguards pass: action/label consistency, per-head uncertainty filtering, independent snapshot features, private-data rejection and grouped-origin restrictions. The older failing-filter handoff is superseded by current code/tests.
- Four MLP configurations plus two seed repeats exist under `models/admission-grid-nov10/`. Selected configuration's validation average precision is about 0.7755 versus embedding logistic 0.8674; all six MLP trials report F1 0.8571 on only 18 known validation rows. The MLP has no demonstrated superiority.
- Selected seed-17 checkpoint has a recorded fresh-process reload with zero difference. Today's offline loader also loaded it and produced two bounded probability scores. A fresh fictional milestone scored 0.378 and “Okay, thanks.” scored 0.424; this is a two-line diagnostic, not an accuracy estimate, and reinforces that live usefulness is not validated.
- Reports label the models `pipeline_trial_only` / `suggestion_only_not_integrated`. Training occurred before this audit; no new training was run. Final test metrics were not computed by this audit. Origin grouping remains exploratory with shared authorship/template limitations.
- The latest milestone does not require further training. Showing the neural contribution as an experimental score preview is credible; claiming validated autonomous memory selection is not.

### Three separate chat paths

1. `neurobrain-test` / `chat.py`: general local Qwen chat with rule-based thinking selection and truncation checks. No database retrieval or saving. Open WebUI connected directly to Ollama bypasses the adaptive launcher.
2. `chat_api.py`, model `neurobrain-memory`: authenticated loopback endpoint over the local observation database; last complete question only; cited excerpts/no-evidence; no conversation resolution, tools or image inputs. HTTP tests cover authentication/discovery/framing/deletion. Open WebUI viewing remains unverified.
3. Older basic web UI: local import/search/inspect/forget. Its historical browser walkthrough does not validate the newer Open WebUI flow.

The general-chat 14-prompt authored development results were 11/14 fast and 12/14 thinking/adaptive. They are not broad accuracy measurements; adaptive timings reused paired calls. Later 8,192-token thinking / 2,048-token fast terminal limits and 16,384 context changed after that evaluation. Historical 13-part completion testing took 147.64 seconds thinking and 19.11 seconds fast; completion did not guarantee correctness. These settings do not change `extract.py`'s separate 60-second timeout or extraction budgets. Qwen is pretrained with prompt/runtime customization, not a newly fine-tuned generator.

## Checks performed during this audit

| Check | Result |
|---|---|
| Full Python unittest discovery, offline encoder flags | 61 discovered; 59 passed, two HTTP tests blocked by sandbox socket binding; no skips |
| Scoped loopback reruns | `test_interfaces.py` 3/3 and `test_chat_api.py` 2/2 passed; both blocked tests resolved, all 61 unique tests passed across runs |
| Deterministic temporary-database demo | Eight steps passed; temporary data removed |
| Frozen corpus count/hash and trial reports | Verified directly; no final evaluation or training |
| Offline selected MLP inference | Loaded and scored two fictional lines; bounded scores, no usefulness acceptance claim |
| Fresh real-Qwen extraction → temporary storage → answer → delete check | **Failed at first extraction: HTTP read timeout after 60 seconds on one short fictional sentence.** Later storage/answer/deletion stages were not reached. Temporary directory cleaned up. |
| Follow-up Ollama metadata | Version 0.40.16 responded; `/api/ps` returned no loaded models. Root cause of timeout not established; cold-load/runtime state needs investigation. |
| Ruff check | Available now, but five findings in `chat.py` / `test_chat.py` (RUF001 and RUF005); not fixed during audit |
| `git diff --check` | Passed |
| Hosted SQL/cloud and UI/capture | Not rerun; `psql` unavailable in this shell. No hosted credentials used, no screen capture or UI changes made. |

Passing mocked component tests does not establish live model, account, OS capture or UI reliability. Offline MiniLM loaded successfully; no network-blocked full-workflow test or representative 10k-chunk latency/RAM benchmark was performed. Hosted functionality necessarily requires network access.

## Next work, in priority order

1. **13–14 November: restore a dependable local vertical slice.** Diagnose the fresh extraction timeout on the presentation Mac; record cold/warm behavior. With a new fictional file and temporary demo DB, require extract → save → restart → cited answer → no-evidence → forget → restart to pass. Preserve lexical fallback. Do not merely increase every timeout or assume chat settings fix extraction.
2. **14–16 November: prove the actual sources and UI.** In a supervised session, verify one selected Notion page, one saved Markdown file and an unsaved VS Code fact. Confirm screen permission and denied app/window behavior. Connect Open WebUI to `neurobrain-memory` using the same DB/root; verify citation rendering, deletion and unavailable-service errors. Record live outcomes separately from automated tests.
3. **14–17 November: close the required hosted gap.** Extend the hosted observation contract for source/app/route/window-session/evidence and policy provenance, then connect observations and retrieval to it. Verify one signed-in acknowledged commit and fresh-process read before expanding coverage. Exercise per-user isolation, retries without duplication, versions, deletion and unrelated-note retention. The existing Drive RPC alone does not satisfy the two-app observation demo.
4. **16–19 November: make saving and rejection honest.** Use a supervisor-reviewed fictional fixture table for keeps, transient skips, ambiguity/abstention and explicit privacy rejection. Require no rejected text in retained stores/logs. Add cross-route deduplication and genuine-change versioning. If autonomous admission cannot meet this gate, propose an explicitly reviewed/manual save demo; that is a scope reduction from the current automatic-save contract and must be agreed, not silently relabeled complete.
5. **19–21 November: measure and freeze.** Measure source-change-to-acknowledged-commit for each route (plan target: five seconds); record actual latency and timeout rate. Test disconnection, permission changes, pause/stop during inference, restart, forbidden markers and hosted owner isolation. Address the five lint findings, freeze dependencies/config/model identifiers and repeat regressions after fixes.
6. **21–22 November: prepare presentation evidence.** Create a short deck, an exact five-minute command/UI run sheet, expected-result fixture table, read-only database queries, current architecture diagram and a recorded successful run as backup. Rehearse on 22 November with fresh fictional markers and valid credentials; present on 23 November. Fix stale status statements in the plan/session log/checkpoint using actual evidence.

## Minimum credible presentation

**Required to satisfy the current milestone:** approved Notion + VS Code workflow, including one unsaved screen fact; exact source-supported typed notes; independently visible acknowledged hosted rows; cited answer and no-evidence through the agreed interface; negative skip/ambiguity/privacy cases; paused/denied capture; update/dedup; restart; forget with unrelated evidence retained. Show actual timing and source provenance. A signed-in hosted rehearsal and real window acceptance cannot be replaced by mocks.

**Credible smaller fallback:** selected fictional file → local extraction and SQLite → inspect evidence → cited answer/no-evidence → source update → forget/restart, with the deterministic eight-step demo available if Ollama is unavailable. This is already substantially implemented, but its model-backed version currently has a timeout blocker. A local-only fallback does not fulfill the documented hosted/two-app acceptance; explicitly agree a reduced scope if needed.

**Defer:** Qwen fine-tuning, adaptive Open WebUI routing, a new frontend, a third application/optional Drive route, broad autonomous desktop capture, knowledge-graph/temporal reasoning extensions, public benchmark expansion and research-scale optimization. Keep final admission test data reserved until the selection protocol calls for it; prioritize the working evidence loop over more model training.

**Unverified:** live capture, Notion accounts, hosted writes and Open WebUI acceptance were not exercised here. The main risk is that passing component tests conceal runtime/integration failures; today's extraction timeout is direct evidence of that gap.
