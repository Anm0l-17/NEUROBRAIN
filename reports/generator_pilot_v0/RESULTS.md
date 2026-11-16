# Qwen-based NeuroBrain generator pilot — 13 November 2026

Decision: **training pipeline passed; expansion gate failed**. Keep the original NeuroBrain runtime active. This adapter is experimental and has not been deployed.

## What actually ran

- MLX-LM 0.32.2 / MLX 0.32.4 in an isolated environment on Apple Metal.
- Pinned `mlx-community/Qwen3.5-4B-4bit` revision `0e7ffd5c629ef7719d4cbc04069232580bfa9d9c`, text-only use.
- Five training examples and three development examples adapted from PersonaMem-v2's public training preview. Targets were authored for evidence-grounded recall, abstention and forget handling; these are not the upstream answer targets. Attribution: bowen-upenn/PersonaMem-v2, CC-BY-4.0; modifications recorded in the data manifest.
- Distinct train/development personas; all tokenized examples below 1,024 tokens, so no context truncation.
- QLoRA: 20 iterations, one final layer, rank 8, learning rate 0.0001, seed 17, batch size 1, prompt masking and gradient checkpointing. 0.479 million trainable parameters, about 0.011% of model parameters.
- Adapter saved to `models/generator-pilot-v0/adapters.safetensors` and reloaded in fresh processes for loss and generation. Model weights are ignored by Git; no commit, upload, or production replacement.

## Results

| Check | Baseline | Adapter | Meaning |
|---|---:|---:|---|
| Development completion loss, fresh process | 2.215 | 1.674 | Better likelihood of these three authored answers; not a general quality score |
| Requested citation marker present | 1/3 | 3/3 | Formatting improved; marker presence alone does not prove grounding |
| Correct final abstention/conclusion, manual review | 3/3 | 3/3 | Both models reached the right high-level conclusions |
| Unsupported speaker attribution, manual review | 0/3 | 1/3 | Regression: adapter called assistant-authored text a user statement |
| Checkpoint save/reload | N/A | Passed | Local training is operational |
| Full dataset / cross-dataset performance | Not run | Not run | No basis for broad superiority claims |

The third adapter answer says the user refers to “the past few weeks at the hospital.” In the supplied evidence, that sentence is in an assistant draft. Its final refusal to infer hospital employment is appropriate, but the attribution is still wrong. This violates the pilot's requirement to distinguish user statements from assistant drafts.

The in-training validation log improved at iteration 10 and worsened by iteration 20. Do not interpret falling training loss as continual improvement. The quoted comparison above uses separately loaded baseline and final adapter evaluations; the CLI calls this `Test loss`, but `test.jsonl` is explicitly an alias of the three development rows, not an independent final test.

Timing is retained per answer in the JSON outputs. Three different-length generated answers are not a retrieval-latency benchmark. No claim of faster retrieval or continual learning is supported by this experiment.

## Review and next session

CodeRabbit raised one major issue: a fixed temporary model path made the evaluation script non-portable. Fixed by accepting and validating a local model path. Review output is saved in `coderabbit.ndjson`. The change was checked by rerunning adapter generation. The automated review is a code review, not independent validation of training labels or model quality.

Next: add training-only examples of assistant drafts, quoted third-party statements, explicit corrections and uncertain ownership, then repeat baseline comparison on a larger disjoint development set. Retain the original failures as development regressions; they can no longer count as an untouched final evaluation. Select a candidate using development results before opening a separate final holdout.

The user's chart assigns LifeDialBench, MemoryAgentBench and PerLTQA to evaluation, and PersonaMem-v3 to observation-data inspection. It does not justify merging all benchmark answers into training. If later adapting any of these for training, first reserve disjoint users/documents/tasks for evaluation, verify terms, and disclose the modified split. Benchmark test answers must not serve as both lessons and an independent exam.

## Reproduction

Run from the repository root. The pinned model and training environment currently live in `/private/tmp` and may be cleaned by the OS. Dependency versions are in `requirements.lock.txt`; the model revision and parameters are in `run_metadata.json`. Recreate the environment and download that exact revision if needed.

```sh
/private/tmp/neurobrain-qwen-pilot-venv/bin/python -m mlx_lm lora --model /private/tmp/neurobrain-qwen35-4b-mlx --data data/generator_pilot_v0 --train --iters 20 --num-layers 1 --batch-size 1 --learning-rate 0.0001 --max-seq-length 1024 --mask-prompt --grad-checkpoint --steps-per-report 5 --steps-per-eval 10 --val-batches 3 --save-every 20 --seed 17 --adapter-path models/generator-pilot-v0
/private/tmp/neurobrain-qwen-pilot-venv/bin/python reports/generator_pilot_v0/generate_answers.py /private/tmp/neurobrain-qwen35-4b-mlx models/generator-pilot-v0 reports/generator_pilot_v0/adapter_answers_recheck.json
```

For baseline generation, pass an empty string as the adapter argument. For development loss use `mlx_lm lora --test --batch-size 1 --test-batches -1 --max-seq-length 1024 --mask-prompt` with the same model/data paths and the relevant adapter path (empty for baseline).

Limitations: tiny assistant-authored teaching set, one seed, no final holdout, no independent human label review, no retrieval integration, and no production inference/export validation. The pilot is useful evidence that training works, not evidence of a better general assistant.
