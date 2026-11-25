# Citation selector v1 — baseline before training (25 Nov 2026)

Base `qwen3.5:4b` (Ollama, temperature 0, the app's exact request from `extract.selection_payload`) on the
sealed evaluation set `data/selector_v1/eval_sealed.jsonl` (359 rows, 1 to 5 evidence lines each like the app's
search; 122 rows have no answering line). Scoring follows the app's acceptance rule: a reply with an unknown ID,
more than five IDs or a malformed list counts as an error and a miss. Raw: `base_eval.json`, 776 s.

| Source | Rows | Exact match | Abstain recall | Abstain precision | Over-select | Under-select |
|---|---|---|---|---|---|---|
| All | 359 | 0.435 | **0.172** | 0.955 | 0.122 | 0.397 |
| SQuAD 2.0 | 150 | 0.447 | 0.156 | 0.933 | 0.100 | 0.083 |
| HotpotQA | 94 | 0.245 | 0.105 | 1.000 | 0.173 | 0.680 |
| LongMemEval | 100 | 0.530 | 0.143 | 1.000 | 0.108 | 0.409 |
| Demo fixtures | 15 | 0.867 | 0.667 | 1.000 | 0.000 | 0.000 |

The main weakness is abstention: when no line answers the question, the base model still cites one 83% of the
time. On the demo fixtures it passes all 9 answerable questions and fails 2 of the 6 near misses ("Saffron Bridge
launch party" with four lines shown, and "amber lighthouse party"). Earlier builds of this set (fixed five lines,
then looser answer filters) gave abstain recall 0.076 and 0.118; the numbers here supersede them.

Definitions: exact match = predicted citation set equals the gold set. Abstain recall = share of no-answer rows
where the model returned no citation; abstain precision = share of empty predictions that were correct.
Over-select = answerable rows with at least one wrong extra citation; under-select = answerable rows missing a
gold citation (HotpotQA needs two or three).

## Training plan

`kaggle/selector_train.ipynb` trains a QLoRA adapter (rank 16, all language-model attention, linear-attention
and MLP projections) on `train.jsonl` (3,000 rows, 36% empty targets) and scores base vs adapter on `dev.jsonl` (295 rows).
The sealed set is never downloaded on Kaggle.

## Converted base (the comparator) and deployment check

`neurobrain-selector-base`: HF Qwen3.5-4B @ 851bf6e → `convert_hf_to_gguf.py` from llama.cpp `1a0b56c`
(the last commit before qwen tensors were fused; the newest converter writes `ssm_beta_alpha` and
`attn_qkv_gate`, which Ollama 0.40.16's runtime rejects) → `llama-quantize Q4_K_M` → `ollama create` with the
official `qwen3.5` renderer and parser (`scripts/selector.Modelfile`). Raw: `converted_base_eval.json`, 826 s.

| Model | Exact match | Answerable exact | Abstain recall | Abstain precision | Over-select |
|---|---|---|---|---|---|
| Official `qwen3.5:4b` (nvfp4) | 0.435 | 0.570 | 0.172 | 0.955 | 0.122 |
| Converted base (Q4_K_M) | 0.443 | **0.536** | **0.262** | 0.889 | 0.101 |

Conversion alone changes behaviour (more abstaining, fewer exact answers), which is why the gate compares the
adapter with the converted base. Both fail the same two near-miss fixtures.

Deployment rehearsal: `scripts/deploy_selector.sh` merged a zero-initialised LoRA with the training targets
(30.5 M parameters: 24 linear-attention, 8 full-attention and 32 MLP blocks, vision excluded), converted,
quantized and created it in Ollama. The quantized file was byte-identical to the converted base and gave
identical answers on 30 of 30 sealed rows, so a trained adapter can reach the app by this route.

## Promotion gate (fixed before any adapter result exists)

The comparator is the **converted base**: unmodified HF Qwen3.5-4B taken through the same merge → GGUF →
quantize → `ollama create` route the adapter will use, scored with `scripts/eval_selector.py`. The official
nvfp4 `qwen3.5:4b` numbers above only describe today's app. The adapter, served the same way, is promoted only
if on the sealed set:

1. Abstain recall is at least **0.50** (converted base 0.262; official 0.172).
2. Abstain precision is at least **0.85** (it must not refuse real questions to get there).
3. Exact match on answerable rows is at least **0.516** (converted base 0.536 minus 0.02).
4. All 9 answerable demo fixtures still pass, and at least 5 of the 6 near-miss fixtures return no citation.
5. No parse or request errors.

If it misses any item, the adapter stays an experiment and the app keeps the official model.

## Adapter v1 result: not promoted

Kaggle T4 run (data commit `b5d9674`, seed 17, 375 optimizer steps over 3,000 rows, 7,208 s, peak 7.8 GiB);
training loss fell from 0.082 (first tenth) to 0.013 (last tenth). On `dev.jsonl` the adapter scored exact 0.780,
abstain recall 0.991, abstain precision 0.772 (3 parse errors). Deployed with `scripts/deploy_selector.sh` as
`neurobrain-selector-v1` (adapter keys matched before merge). Sealed set, raw `adapter_eval.json`, 640 s:

| Model | Exact match | Answerable exact | Abstain recall | Abstain precision | Over-select | Errors |
|---|---|---|---|---|---|---|
| Converted base | 0.443 | 0.536 | 0.262 | 0.889 | 0.101 | 0 |
| Adapter v1 | 0.674 | 0.515 (122/237) | **0.984** | **0.571** | 0.059 | 0 |

| Gate item | Needed | Adapter v1 | Result |
|---|---|---|---|
| 1. Abstain recall | ≥ 0.50 | 0.984 | pass |
| 2. Abstain precision | ≥ 0.85 | 0.571 | **fail** |
| 3. Answerable exact | ≥ 0.516 | 0.515 (122/237) | **fail** (by one row) |
| 4. Fixtures | 9/9 answerable, ≥ 5/6 near-miss abstain | 9/9, 6/6 | pass |
| 5. Errors | 0 | 0 | pass |

The adapter fixes the demo problem (all six near misses, including "Saffron Bridge launch party" and "amber
lighthouse party", now return no citation) but overcorrects: it returns nothing on 90 of 237 answerable rows
(38%; base 1.7%), most on LongMemEval (40, abstain precision 0.149) and SQuAD 2.0 (38). The higher overall exact
match comes from the many no-answer rows. Per the gate it stays an experiment; the app keeps `qwen3.5:4b`.
Dev abstain precision (0.772) already pointed this way, and the sealed set is harsher. Likely next steps: fewer
empty targets than the current 36%, or more LongMemEval-style answerable rows; a v2 needs a new sealed set or an
untouched slice, since this one has now been used for a gate decision.

## Admission MLP v2 (same day)

`scripts/train_admission_v2.py`, report `reports/admission_v2/report.json`. Adding 4,004 LoCoMo turns
(labels from LoCoMo's model-generated observations; 10 conversations, split 7/1/2 by conversation):

| Train on | Test | MLP AP | Logistic AP |
|---|---|---|---|
| Ours only (1,422) | Ours (48) | 0.730 | 0.806 |
| Ours only | LoCoMo (1,198) | 0.453 | 0.531 |
| LoCoMo + ours | Ours | 0.797 | 0.851 |
| LoCoMo + ours | LoCoMo | 0.584 | 0.638 |

More data lifts the MLP (0.730 → 0.797 on our test, 0.453 → 0.584 on LoCoMo), but the embedding-logistic
baseline still wins every comparison, so the MLP stays advisory and the logistic model is the better preview
scorer. Limits: our 1,584 rows come from only three template families, so "ours" train, validation (18 rows)
and test (48 rows) are each one family; the 48-row test, reserved since v1, has now been used and is no longer
untouched. LoCoMo has 10 conversations, so its test is two conversations. Treat these numbers as small-sample.
