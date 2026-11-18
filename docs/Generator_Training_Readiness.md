# NeuroBrain generator training: first experiment

Prepared 13 November 2026. Status: a 20-step Qwen3.5-4B QLoRA pilot completed and its adapter reloaded. Expansion is blocked by a speaker-attribution regression. See [pilot results](../reports/generator_pilot_v0/RESULTS.md).

## What exists today

`ollama/Modelfile` uses `qwen3.5:4b` with a NeuroBrain system prompt and runtime settings. This is not a trained adapter or a new set of model weights.

The checked local corpus, `data/admission_reviewed_exploratory_v0_1.jsonl`, contains 1,584 admission examples: 1,500 train, 24 validation, 60 test. Its fields include candidate text, prior context, and an admission label. It is not an approved conversational fine-tuning corpus. These splits belong to the admission experiment; they do not establish a generator evaluation set.

The original project environment remains unchanged. A separate temporary environment now has MLX-LM 0.32.2 and MLX 0.32.4; Apple Metal training and adapter reload succeeded. See the pilot dependency lock for reproducibility.

## Small first training cycle

1. Inspect the dataset plan and actual files. Record source URL, revision, license, intended use, row count, and any personal information. Agree on the first behavior to improve: for example evidence-grounded answers, extraction, or conversational style.
2. Review representative examples and define the input and expected output. For evidence tasks, include the evidence in the input and ensure the target cites only identifiers present there. Include examples where the correct response is to abstain.
3. Split by source document, conversation, person, or scenario family before generating variants. Keep duplicates and paraphrases together. Reserve a final test set; never use its answers for training or iterative prompt tuning. Keep existing designated evaluation benchmarks out of training.
4. Run the unchanged Qwen baseline on the development set with the same retrieval inputs and generation settings that will be used for the adapted model. Save outputs and latency.
5. Verify an architecture-compatible trainer for the exact Qwen checkpoint, tokenizer/processor, and chat template in a separate environment. Test one forward/backward update and save/reload on a tiny approved training subset before launching a full run. Record peak memory and elapsed time.
6. Train one small adapter experiment. Record dataset hashes, base-model revision, package versions, seed, training parameters, and checkpoint path. Keep the original runtime available for rollback.
7. Evaluate the adapter against the baseline on the development set. Review failures, revise training data or settings, and repeat. Use the reserved final test only after selecting the candidate.

## Review gates

| Gate | Technical evidence | Plain-language meaning | Current status |
|---|---|---|---|
| Dataset suitability | Inspected schema, provenance, license, reviewed targets | We know what the model will learn | Tiny adapted v2 set checked; full corpus pending |
| Split integrity | Group separation and duplicate checks | The exam answers are not in the lessons | Tiny pilot personas disjoint; full corpus pending |
| Baseline | Saved outputs and task-specific scores | We know how the original model performs | Baseline completed on three pilot development cases |
| Runtime | One training update and checkpoint reload | The computer can actually train this model | Passed for tiny pilot |
| Candidate quality | Same-input baseline comparison, error review | Training produces a measurable improvement | Failed attribution guardrail; do not expand |
| Demo integration | Fresh VS Code/Notion observation, retrieval, cited response | The professor sees the newly entered fact recalled | Separate integration gate; training does not prove it |

Set acceptance thresholds before training once the task and data are known. For evidence tasks, measure answer correctness, citation validity, unsupported claims, and abstention separately; also record latency and ordinary-chat regressions. A lower training loss alone is not a promotion criterion.

## Boundaries

Fresh user notes belong in external memory and retrieval. Do not retrain for every newly entered fact. A successful trained version can be called a Qwen-based NeuroBrain fine-tune, with the base model and adaptation disclosed. Claim improvement only on the tasks actually evaluated.

PersonaMem-v2 is the first training candidate; the inspection findings below must be resolved before constructing training examples. Isolated training dependencies and a pinned 2.9 GB MLX checkpoint were downloaded. Tiny-pilot training works; full-corpus capacity and quality remain unverified.

## Dataset decision after source inspection

| Candidate | Intended role | Verified source and limits |
|---|---|---|
| PersonaMem-v2 | First training candidate, text partitions only | [Official card](https://huggingface.co/datasets/bowen-upenn/PersonaMem-v2): CC-BY-4.0, published train/validation/benchmark partitions. Verify actual persona separation and row counts after downloading pinned files. |
| PersonaMem-v3 | Cross-app observation evaluation and adaptation research | [Official card](https://huggingface.co/datasets/bowen-upenn/PersonaMem-v3): CC-BY-NC-4.0. Keep benchmark queries reserved initially. Inputs must exclude inferred preference labels and scorer answers; events must precede each query timestamp. |
| LifeDialBench | Ambient-dialogue evaluation | [Official repository](https://github.com/RayNeo-AI-2025/LifeDialBench): EgoMem/LifeMem JSON released; evaluation scripts described as forthcoming. Dataset license not established in this inspection. |
| MemoryAgentBench | Incremental retrieval, learning, conflict and long-range evaluation | [Official dataset](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench): MIT metadata, with multiple upstream datasets; check component provenance before redistribution. Do not use benchmark answers for training. |
| PerLTQA | Supplementary structured personal-memory evaluation | [Official repository](https://github.com/Elvin-Yiming-Du/PerLTQA): CC-BY-NC-4.0; use the updated release and record its revision. |

### Actual v2 preview inspection

Downloaded the Hugging Face dataset-server `first-rows` response for `config=benchmark`, `split=train_text`. Saved to `reports/personamem_v2_inspection/train_text_preview.json`: 21 preview rows, SHA-256 `17548235bc6cc608d687ce0b9c57b4aed30c58bab5714043be67f3da68736b22`. This is an unpinned preview, not a reproducible training release or a representative quality audit. Manually inspected the first two examples.

- `user_query` is a serialized Python-style dictionary in the inspected rows; the related snippet is serialized JSON. Do not use `eval` when converting either field.
- The first row, persona 13, has a target mentioning a medication budget and support group absent from its related snippet. Full history may supply these details; snippet-only training would not establish them. Resolve support from the actual input before accepting the target.
- The second inspected row contains an explicit request to forget an interest. Preserve that temporal instruction when constructing inputs; simply extracting the earlier interest would produce the wrong behavior.
- Fields such as expanded persona, preference, correct answer, and incorrect answers are annotations, not observations to feed a model during evaluation. A related-snippet-only test is an oracle-context diagnostic, not end-to-end retrieval evaluation.

Next experiment scope: curate a small batch from the official text training partition after checking full-history support, then use official validation personas for development. Keep the benchmark partition untouched. Do not merge all five datasets into a training pool.


## Attribution repair follow-up
The requested small attribution repair and retest is complete: **NO, not a pass**. The repaired adapter met all criteria on 7/9 development cases, equal to the previous adapter, with different failures. No scaling or deployment is authorized. See [full retest](../reports/generator_pilot_v1/RESULTS.md).
