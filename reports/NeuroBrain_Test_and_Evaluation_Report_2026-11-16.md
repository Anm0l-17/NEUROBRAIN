# NeuroBrain Testing and Evaluation Report

**Evidence cutoff:** 16 November 2026  
**Scope:** Results recorded in the repository. This report distinguishes software tests, integration demonstrations, model evaluations, manual data review, and unrun checks. A pass on a small fixture is not evidence of general accuracy or release readiness.

## Executive summary

- **Local deterministic memory:** Initial implementation gates passed: 15/15 unit tests plus lint, formatting, compilation, build/install, demo and a scoped browser walkthrough. Baseline fictional QA passed 6/6 cases, including deletion and abstention.
- **Hybrid retrieval:** Reported Recall@5 was 1.0 for lexical and semantic retrieval on just two fictional paraphrase queries. This is a smoke-sized result.
- **Current application tests:** A recorded full suite on 13 November passed 68/68 tests. An earlier overnight run passed 61/61 unique tests after two network tests were rerun with loopback permission. These are different snapshots, not additive unique test counts.
- **Real local model workflow:** Two fictional extraction→save→restart→answer→update→forget demonstrations passed in 5.110s and 5.173s. Separate extraction prompt experiments exposed significant ambiguity and timeout failures.
- **Admission classifier:** Exploratory fitting and reload checks worked, but the held validation set has only 18 binary labels and the embedding logistic baseline outscored the MLP in reported average precision. Data origins are not independent enough for generalization claims. No admission model is accepted for automatic saving.
- **Qwen generator:** Results are mixed and promotion gates failed. The compact Kaggle adapter scored 8/9 versus base 6/9 on an authored development suite; an expanded instruction later scored adapter 9/9 on the old suite but only 4/6 on new probes and introduced a new ownership error. A separate repaired adapter tied the previous adapter at 7/9 and introduced attribution failures. No candidate is promoted.
- **Chat mode routing:** On 14 authored prompts, fast passed 11/14, always-thinking 12/14, adaptive 12/14. Four follow-up development prompts passed 4/4 after a routing fix, but one failure informed that fix; these are not held-out results.
- **Important failures still visible in the record:** ambiguity accepted as a memory, assistant text attributed to the user, generation timeouts, wrong country answer, instruction wording miss, and a Kaggle cell failing before training with `NameError: original is not defined`.
- **Not established:** live Notion and unsaved VS Code capture acceptance, hosted Supabase end-to-end use, Open WebUI acceptance, broad benchmark quality, reliable 10k-chunk performance, or deletion of every possible backup/replica.

## 1. Application and software checks

### 1.1 Initial deterministic memory release checkpoint — 27 October

Source: [`verification.md`](verification.md)

| Check | Result |
|---|---|
| Unit/regression suite | **PASS 15/15** |
| Ruff lint | **PASS** |
| Ruff formatting | **PASS**, eight files already formatted |
| Python compilation | **PASS** |
| Wheel build and install | **PASS**; installed `neurobrain --help` worked |
| Clean temporary environment install | **PASS**; imported fixture, queried SQLite and loaded packaged HTML |
| Repeatable demo | **PASS**, eight steps, including restart and duplicate-import suppression |
| Browser walkthrough | **PASS, scoped**: search/citations, deletion preview/confirm, forgotten result absent, unrelated source retained |
| Browser rendering | **PASS, desktop only**; forms/evidence rendered and no console errors after reload |
| Static typing / coverage | **NOT MEASURED** |
| Full security audit / hostile concurrent filesystem attacks | **NOT RUN** |

The tests covered exact Unicode spans, edited-source versioning, all-version forget and restart, tombstones/reimport suppression, transaction rollback on import/deletion failures, credential/directive/path/symlink rejection, query scoping, FTS integrity, CLI/HTTP behavior, and mutation protections. They used fictional notes. Neural training, semantic retrieval, temporal reasoning, generation quality, backups/forensic erasure, mobile compatibility, offline-network behavior, and scale were explicitly outside this gate.

### 1.2 Baseline functional evaluation — 2 November

Source: [`baseline_v0.json`](baseline_v0.json)

- Fictional cases: **6 total; all passed** (5 answerable and 1 unsupported).
- Answerable recall: **1.0**.
- Unsupported-query abstention: **1.0**.
- Citation validity: **1.0**.
- Deletion canary: receipt verified, deleted evidence absent after deletion, unrelated retained evidence still retrievable.

This is a small lexical/extractive lifecycle benchmark. It does not measure semantic search, generated answers, temporal reasoning, or real-user behavior.

### 1.3 Hybrid semantic retrieval — 3 November

Source: [`semantic_v0.json`](semantic_v0.json)

- Pinned encoder: `sentence-transformers/all-MiniLM-L6-v2`.
- Lexical Recall@5: **2/2 (1.0)**.
- Semantic Recall@5: **2/2 (1.0)**.
- Fallback: not invoked in this run.

The cases were two fictional paraphrase lookups. Passing both is a working-path check, not evidence semantic retrieval beats lexical search on a representative corpus.

### 1.4 Recorded Python regression suites

| Checkpoint | Result recorded | Notes |
|---|---:|---|
| 27 Oct initial prototype | **15/15 passed** | See above. |
| 2 Nov baseline gate | **23/23 passed** | Full unittest suite, plus Ruff lint/format and evaluation. |
| 3 Nov hybrid retrieval checkpoint | **30/30 passed** | Full suite, offline semantic experiment; Ruff/Ralph checks passed. |
| 9 Nov readiness review | **34 passed, 1 failed** after a separate socket-permission rerun | One real uncertainty-selector failure remained then; socket issue resolved by rerun. Expected 79 usable filtered examples, observed 0. This was later addressed in the recorded 68-test suite, but the earlier report remains historical evidence. |
| 13 Nov overnight full suite | **61 unique tests passed** | Initially 59 passed and 2 HTTP tests were blocked by sandbox loopback binding; scoped permitted reruns passed 3/3 and 2/2. No skips. |
| 13 Nov later full suite | **68/68 passed** | `reports/overnight_2026_11_13/current_regression.txt`; 1.635s. Includes admission assembly/grouping/release, chat/API, cloud import, extraction, interfaces, memory, observation, screen, semantic fallback/model, and training-data validation. |

In the 68-test run, the previously problematic uncertainty behavior is tested by `test_uncertain_action_is_kept_as_ambiguity_not_binary_label`, plus action filtering and label consistency checks. Passing this unit test does not erase the prior bug; it shows the tested current code path passed in that snapshot.

Other recorded quality checks: Ruff and format checks, `git diff --check`, compile/build checks on earlier snapshots. At the 13 Nov readiness audit, Ruff had five findings in `chat.py` / `test_chat.py`; later progress reports state Ruff was clean after fixes. Avoid assuming every newer dirty-worktree change was covered by these historical checks.

### 1.5 Local model-backed workflow demonstration — 13 November

Sources: [`local_demo_01.json`](overnight_2026_11_13/local_demo_01.json), [`local_demo_02.json`](overnight_2026_11_13/local_demo_02.json)

Both temporary-database runs passed all scripted assertions in **5.110s** and **5.173s**. They exercised fictional extraction and save, restart, citation, duplicate handling, updated extraction/versioning, forget across versions, and preservation of unrelated evidence. Temporary databases were removed.

A separate earlier readiness probe failed: one short fictional sentence did not complete extraction before a **60-second HTTP read timeout**. Later successful runs prove the path can work; they do not establish that the timeout root cause was fixed or quantify reliability. Live capture, cloud, accounts and Open WebUI are not covered by these local demos.

## 2. Extraction quality and failure probes

Sources: `reports/extraction_*_2026_11_11.json`

All cases were developer-authored prompt-development checks using local Qwen3.5-4B, not independent or held-out evaluation.

| Probe set | Outcome |
|---|---|
| Initial six-case smoke | **5/6 passed**. Clear milestone/decision extracted, chatter empty, privacy directive and possible credential blocked. **Failed:** vague “Move that to there after the thing is finished” was saved as a preference. |
| Follow-up example set | Clear decision passed; ambiguity and unresolved references such as “Please send it to her tomorrow” and “It is broken again” were incorrectly turned into memory candidates. |
| Context prompt revision | Improved “It is broken again” to empty while contextual pronoun and clear decision cases passed; ambiguous/missing-object references still failed. |
| Reasoning-enabled prompt | **Failed operationally:** several requests timed out at roughly 60 seconds; ambiguity and missing-object cases still failed, and a valid clear decision produced no completed extraction. |

The later 68 software tests validate extraction validation, privacy ordering, evidence offsets, malformed/invented evidence rejection and lifecycle handling using test doubles/fixtures. They do not establish model extraction quality on varied real inputs.

## 3. Admission dataset and classifier evaluation

Sources: [`admission_reviewed_v0_2.md`](admission_reviewed_v0_2.md), [`admission_semantic_grouping.md`](admission_semantic_grouping.md), [`admission_start_v1/report.json`](admission_start_v1/report.json), [`admission_baselines_v1/report.json`](admission_baselines_v1/report.json)

### 3.1 Corpus and overlap checks

- Consolidated v0.2: **1,584 fictional reviewed records** — 960 keep, 528 skip, 96 uncertain actions. Uncertain action rows retain null binary labels.
- Of the 1,500 A/B/C records, exact normalized duplicate candidate excess was **0**. Semantic screening at candidate cosine ≥0.85 flagged **3 pairs** (one cross-batch); context threshold ≥0.90 flagged **0**.
- Despite low exact duplication, all 1,500 A/B/C rows remained one connected shared template/origin component. Fresh01 (24 rows) and Fresh02 (60 rows) are provisional authoring groups, not proven independent origins. Fresh02 repeats a fixed scenario label pattern.
- Thus the split is explicitly marked **exploratory, not an independent release**. Similarity screening is not proof of independent origin.

### 3.2 Exploratory training-path / reload check

- Frozen exploratory file hash: `d91b7314…b192dab1`; seed 17, 32 AdamW steps.
- 16 training examples used in the start-gate diagnostic. Reviewed-label loss changed **0.5146 → 0.4003**; permuted-label loss **0.5145 → 0.4034**. The permuted-label run demonstrates fitting capacity, not useful learning.
- Gradients finite, parameters changed, batch/individual features and row-order consistency checked in the report.
- Fresh-process checkpoint reload: **PASS**, maximum absolute prediction error **0.0** (tolerance 1e-6).

This passed an engineering smoke gate only. It did not prove generalization or the classifier should control memory decisions.

### 3.3 Validation baselines

Train partition included 1,422 binary targets. Validation had **18 labeled rows**: 12 keep and 6 skip. Results at validation-selected thresholds:

| Baseline | Precision | Recall | F1 | Average precision | Confusion (TN, FP, FN, TP) |
|---|---:|---:|---:|---:|---|
| Store all / majority | 0.667 | 1.000 | 0.800 | 0.667 | (0, 6, 0, 12) |
| Rules | 1.000 | 0.083 | 0.154 | 0.694 | (6, 0, 11, 1) |
| TF-IDF logistic | 0.667 | 1.000 | 0.800 | 0.751 | (0, 6, 0, 12) |
| Embedding logistic | **0.750** | 1.000 | **0.857** | **0.867** | (2, 4, 0, 12) |

The 18-row validation set is too small for strong claims. The embedding logistic baseline was the strongest reported baseline; this is not evidence the MLP is superior. A later progress report states exploratory MLP validation AP ~0.7755 versus embedding logistic ~0.8674; the six MLP trial F1 values were ~0.8571. Final test labels were reserved in that report and should remain untouched until a predeclared selection protocol. No automatic-admission deployment is supported.

## 4. Chat answer and routing checks

Sources: [`Chat_Accuracy_2026_11_13.md`](Chat_Accuracy_2026_11_13.md), `chat_accuracy_2026_11_12.json`, `chat_holdout_2026_11_13.json`, `chat_completion_2026_11_13.json`

### 4.1 Fourteen authored development prompts

| Mode | Passed | Median time | Total time |
|---|---:|---:|---:|
| Fast | 11/14 | 0.95s | 16.68s |
| Thinking | 12/14 | 35.50s | 600.80s |
| Adaptive auto | 12/14 | 1.07s | 211.93s |

These are correctness, instruction-following and completion checks over authored prompts. Adaptive reuses the selected fast/thinking answer, so its measurement is not an independent inference. Manual review caught an automated false pass: an arithmetic answer included the right computed value but initially stated the wrong final price.

Recorded failures: fast/auto answered Canada for largest country instead of Russia; fast/auto did not use the exact requested phrase “not stated”; always-thinking hit generation limits on a simple note lookup and a long room lookup (~88–89s). The router was adjusted after the room lookup failure.

### 4.2 Follow-up four-prompt routing development set

Initial auto routing passed **3/4**; it misclassified “access code” as programming and timed out at 87.854s. After narrowing programming cues, final responses passed **4/4** (Rome, R-42, 828 rupees, Mia). Two reasoning responses took 18.72s and 13.05s. Because one failure directly informed a router change, this is a development check, not held-out validation.

### 4.3 Long completion prompt

A 13-part combined prompt completed and answered the expected tasks, taking **147.64s** in thinking mode. The result covered geography, cited-note-style abstention wording, temporal updates, quoted prompt injection, arithmetic, logic and code. A fast counterpart was recorded at 19.11s; completion did not mean all answers were correct (the broader per-question scorer and raw JSON should be consulted). These timings are not latency guarantees.

## 5. Generator model training and evaluation

### 5.1 Local MLX pilot v0 — 13 November

Source: [`generator_pilot_v0/RESULTS.md`](generator_pilot_v0/RESULTS.md)

- Qwen3.5-4B 4-bit, MLX-LM 0.32.2 / MLX 0.32.4 on Apple Metal.
- Five training examples, three development examples; 20-step rank-8 QLoRA, one trainable final layer, seed 17. Adapter saved and reloaded in fresh processes.
- Development completion loss: **2.215 → 1.674**.
- Citation marker: **1/3 → 3/3**.
- High-level conclusion/abstention: **3/3 both base and adapter**.
- Unsupported speaker attribution: **0/3 base → 1/3 adapter** (regression: assistant-authored hospital text described as user speech).

**Decision: pipeline passed, expansion gate failed.** Three development rows only; no independent final set, no retrieval integration, no broad quality result.

### 5.2 Local MLX attribution repair v1

Source: [`generator_pilot_v1/RESULTS.md`](generator_pilot_v1/RESULTS.md)

Same pinned base and small training budget; 12 fictional attribution examples added. Nine development cases evaluated with greedy decoding.

| Model | Combined strict criteria | Citation marker alone | Content/attribution alone |
|---|---:|---:|---:|
| Base Qwen | 4/9 | 6/9 | 7/9 |
| Previous adapter | 7/9 | 9/9 | 7/9 |
| Repaired adapter | 7/9 | 8/9 | 7/9 |

Repaired adapter fixed an explicit-confirmation contradiction but newly attributed assistant reflection to the user on the medication case and produced a repetitive, wrong-attribution hospital answer without citation. Validation loss went 2.070 → 1.064 at step 10 → 1.513 at step 20. **No net gain; no scale-up/deployment.** Nine authored development cases, one seed, manual review, no final holdout.

### 5.3 Compact Kaggle QLoRA run — 14 November

Source: [`compact_kaggle_v1/RESULTS.md`](compact_kaggle_v1/RESULTS.md)

- Qwen3.5-4B NF4 on one Tesla T4, 20 masked-target updates, rank 8, seed 17.
- 13 source adaptations from 12 personas; base/adapter comparison on nine development cases.
- Base **6/9**, compact adapter **8/9**; required promotion gate was 9/9 plus improvement, so **FAIL**.
- Main remaining error: fictional screenplay vineyard ownership attributed to user, despite a citation marker.
- Peak allocated GPU memory: 10.64 GiB; adapter 3,674,248 bytes; training cell including setup/generation 148.731s. Timing is not throughput comparison.
- Adapter was reloaded before evaluation. No independent holdout, real-note quality, long-history, general chat or app retrieval/deletion result.
- Code review found the standalone script relied on notebook-defined hashes; packaging was fixed after the training run. The trained weights predate that fix.

### 5.4 Attribution and forget follow-up — 16 November

Source: [`attribution_followup/RESULTS.md`](attribution_followup/RESULTS.md)

| Model/instruction | Original 9 cases | New 6 probes | Complete paired behaviors |
|---|---:|---:|---:|
| Base, original | 6/9 | 5/6 | 2/3 |
| Compact adapter, original | 8/9 | 5/6 | 2/3 |
| Base, expanded | 7/9 | 4/6 | 1/3 |
| Compact adapter, expanded | 9/9 | 4/6 | 1/3 |

The original-prompt models failed fictional courier residence. Expanded prompt fixed the adapter's old vineyard case but newly attributed a fictional radio narrator's occupation to the author and kept courier failure. Both forget probes were interpreted correctly, but no application deletion was tested. New six cases now belong to development regressions.

### 5.5 Candidate retraining attempt after follow-up

Eight proposed hard training examples and six separate final-eval examples were prepared. The Kaggle cell stopped before training with **`NameError: original is not defined`** because the expected notebook variable was absent. **No new candidate adapter was trained or saved.** Final examples must remain untouched until model/prompt selection is complete.

## 6. Dataset review, compute and ancillary checks

- Compact source curation reviewed ten candidate sources and recorded roles, license/provenance and exclusions in `data/neurobrain_shortlist_v1/SOURCES.md`. The admission shortlist contains 200 train IDs (100 keep, 100 skip); it is not a self-contained reviewed training dataset. Two IDs overlap with an earlier admission-start smoke train set. PersonaMem adaptation selected 13 rows across 12 personas; ten decile examples were manually inspected, seven retained and three excluded. This is curation review, not model quality evaluation.
- Full-source acquisition/audit did **not** launch full-corpus training. PersonaMem-v2 train/validation shared 735 personas, requiring persona-level repartition; one benchmark persona overlapped train in the inspected metadata. A MemoryAgentBench context was estimated at 1,683,432 Qwen tokens against a 262,144 position limit; it cannot be passed whole to the model.
- Kaggle access/resource smoke showed two T4 GPUs with 14.56 GiB each and about 19.5 GiB working disk at the time. A synthetic NF4 LoRA update changed adapter weights using 5.47 GiB peak on one T4. This only proved the training path/resources for a synthetic update.
- PostgreSQL SQL scripts for two disposable C2/observation schemas completed transaction-scoped lifecycle assertions and rolled back (`reports/overnight_2026_11_13/postgres_*.txt`). This is local disposable-database evidence, not live Supabase or hosted-auth acceptance.
- Browser deletion walkthrough passed on the local UI; screen/UI observation unit tests passed in the 68-test snapshot. Live unsaved VS Code OCR, Notion account integration, permission transitions and Open WebUI acceptance remain unverified.
- Four CodeRabbit code-scoped reviews recorded 7, 7, 3 and 3 findings, with fixes/dispositions in `reports/overnight_2026_11_13/review_disposition.md`. They are code reviews, not data-label audits, answer-quality evaluations, or comprehensive security reviews.

## 7. Failures, blocked checks and unresolved evaluation risks

### Failed or regressed

1. Vague extraction (“Move that to there after the thing is finished”) was accepted as a preference in initial and revised prompt trials.
2. Missing referents (“Please send it to her tomorrow”) were extracted as preferences in early prompt trials.
3. Reasoning-enabled extraction repeatedly reached the 60s timeout, including on a clear decision.
4. Local generator v0 introduced user attribution of assistant-authored text.
5. Repaired local adapter v1 remained 7/9 and introduced medication/hospital attribution failures.
6. Kaggle compact adapter remained wrong on vineyard owner (8/9 vs required 9/9).
7. Expanded system instruction produced new radio narrator attribution error and only 4/6 new probes.
8. Chat fast/auto: Canada/Russia factual miss and “not stated” instruction miss; thinking could timeout.
9. Admission uncertainty selector had a real failure in an earlier dated run (79 expected usable vs 0 produced); a later software test passed the corrected behavior.
10. Kaggle follow-up candidate run did not execute training due missing `original` variable.

### Blocked, not run, or not evidence-backed

- No independent final generator test has been reported for the current compact adapter; the six prepared final examples have not been used.
- No broad user-facing or public benchmark evaluation of generator, retrieval, chat or admission model.
- No genuine independent admission origins for a strong generalization claim; current validation is 18 binary rows.
- No 10k-chunk latency/memory profile, repeated-seed robustness study, or whole-workflow network-blocked offline test.
- No live end-to-end Supabase/Drive/Open WebUI run or confirmed hosted RLS/deletion parity.
- No accepted live VS Code unsaved-window OCR / Notion observation demo.
- No complete audit proving deletion from backups, exported copies, logs, network buffers and all replicas.
- No current test rerun in this report; cited test totals are historical artifacts from dated snapshots. The current checkout has extensive uncommitted changes, so these counts do not automatically cover every present file.

## 8. Recommended next evaluation work

1. Fix the Kaggle notebook initialization and run a one-batch smoke; ensure the new candidate path cannot overwrite the compact adapter.
2. Train only on the eight reviewed hard examples if their evidence and provenance checks pass. Use the original nine and six follow-up probes for development comparisons; preserve the six final cases.
3. Evaluate base, compact adapter and candidate under identical prompt/decoding. Score content support, owner, citation correctness, abstention/directness and paired behavior separately. Freeze thresholds before opening final cases.
4. Keep the classifier in suggestion-only research. First resolve trainer/data gates, then obtain independent scenario origins and evaluate against simple baselines on frozen partitions.
5. Expand app testing from fixtures to supervised end-to-end checks: source selection/capture, evidence, save, restart, retrieval, forget, residual search, unrelated retention and hosted persistence.

## Evidence index

- Initial implementation gates: [`verification.md`](verification.md)
- Lexical baseline: [`baseline_v0.json`](baseline_v0.json)
- Semantic retrieval: [`semantic_v0.json`](semantic_v0.json)
- Current recorded suite output: [`current_regression.txt`](overnight_2026_11_13/current_regression.txt)
- Local model workflow: [`overnight_2026_11_13/`](overnight_2026_11_13/)
- Admission metrics and grouping: [`admission_baselines_v1/report.json`](admission_baselines_v1/report.json), [`admission_grouped_exploratory_v0_1.json`](admission_grouped_exploratory_v0_1.json), [`admission_overlap/summary.json`](admission_overlap/summary.json)
- Chat evaluation: [`Chat_Accuracy_2026_11_13.md`](Chat_Accuracy_2026_11_13.md) and dated JSON files
- Generator runs: [`generator_pilot_v0/RESULTS.md`](generator_pilot_v0/RESULTS.md), [`generator_pilot_v1/RESULTS.md`](generator_pilot_v1/RESULTS.md), [`compact_kaggle_v1/RESULTS.md`](compact_kaggle_v1/RESULTS.md), [`attribution_followup/RESULTS.md`](attribution_followup/RESULTS.md)
- Historical record: [`session_log.md`](session_log.md)
