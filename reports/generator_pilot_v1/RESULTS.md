# Attribution repair retest

**Overall result: NO — the repaired adapter does not pass. No scaling or deployment.**

The user authorized only strengthening speaker attribution and retesting. Completed a fresh 20-step QLoRA run from the same pinned Qwen3.5-4B base, preserving the prior adapter and live runtime.

## Changes

- Retained five original training examples and added 12 fictional, assistant-authored examples: unconfirmed assistant drafts, third-party quotations, fictional speakers, direct user statements, explicitly confirmed drafts, corrections, updates and forget requests.
- Retained the three previous development cases and added six new scenarios with different facts. These are development checks, not an independent final test. Training and development have no identical examples; task families deliberately overlap.
- Kept seed 17, 20 steps, learning rate 0.0001, rank 8, batch size 1 and one trainable layer. No increase in model size or full-corpus training.
- Reused the evaluation script with an optional dataset-path argument. All three models were evaluated on the same nine cases with greedy decoding, thinking disabled and a 180-token response budget.
- Checked all examples fit within 1,024 tokens without truncation; saved and reloaded the new adapter before testing.

## Nine-case retest

| Case | Original Qwen | Previous adapter | Repaired adapter |
|---|---|---|---|
| No unsupported favorite TV series | Pass | Pass | Pass |
| No medication claim / correct source attribution | Missing citation | Pass | **Fail: assistant reflection attributed to user** |
| Hospital sentence is an assistant draft | Missing citation | **Wrong attribution** | **Fail: repetition, wrong attribution, no citation** |
| Observatory sentence is an assistant draft | Missing citation | Pass | Pass |
| Cousin’s move belongs to cousin | Ambiguous “my cousin” ownership | Pass | Pass |
| Accept direct user employment statement | Pass | Pass | Pass |
| Accept explicitly confirmed assistant draft | Pass | **Contradictory “No”** | Pass |
| Respect user’s correction of assistant | Pass | Pass | Pass |
| Fictional property is not the user’s property | **Wrong owner** | Pass | Pass |
| **All criteria met** | **4/9** | **7/9** | **7/9** |

The combined criterion requires supported content, correct attribution, a coherent answer and the requested citation. Citation-marker presence alone is 6/9, 9/9 and 8/9 respectively. Content/attribution review alone is 7/9 for each model, but with different failures. Baseline “my cousin” is scored strictly as ambiguous ownership; treating it leniently would raise baseline counts by one, without changing the repaired adapter’s failure.

The repaired model fixed the previous adapter’s contradiction on an explicitly confirmed job. However, it introduced an unsupported user attribution on the medication case and produced a long repetitive hospital response. A correct opening “No” does not make that response valid. There is no net improvement over the previous adapter under the declared combined criterion.

Training validation loss moved from 2.070 initially to 1.064 at the iteration-10 check and 1.513 at the iteration-20 check. Those are in-training development measurements, not a substitute for the failed answer tests. Only the final 20-step checkpoint was evaluated for generation; no claim is made about an unsaved intermediate checkpoint.

## Evidence and review

- `baseline_answers.json`, `previous_adapter_answers.json`, `retrained_answers.json`: complete generated answers and timings.
- `assessment.json`: case-by-case manual content judgement and mechanical citation checks.
- `training.log`, `run_metadata.json`, `requirements.lock.txt`: run settings and logs.
- `data/generator_pilot_v1/manifest.json`: origins, data hashes and evaluation criteria. Original v2-derived material retains CC-BY-4.0 attribution; added examples are fictional teaching examples.
- `models/generator-pilot-v1/adapters.safetensors`: experimental adapter, not promoted.

CodeRabbit raised 0 issues in the scoped evaluation-script review; output is in `coderabbit.ndjson`. This is not an independent review of model answers or dataset labels.

## Stop point

Do not scale, merge adapters, replace the deployed model, or start teacher-model training. The user will decide the next approach. A later experiment could investigate a smaller update or earlier checkpoint and better controls for assistant-generated text, but that has not been run here. Teacher–student distillation would train on a teacher’s examples/feedback, not extract private internal sub-networks from a hosted model.

Limits: nine hand-authored development cases, one seed, manual review by the same assistant, no independent final holdout and no retrieval-speed measurement. The result is a failed small regression test, not a general benchmark score.
