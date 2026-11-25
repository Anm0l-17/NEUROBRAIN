# Citation selector v1 — baseline before training (25 Nov 2026)

Base `qwen3.5:4b` (Ollama, temperature 0, the app's exact request from `extract.selection_payload`) on the
sealed evaluation set `data/selector_v1/eval_sealed.jsonl` (365 rows, 1 to 5 evidence lines each like the app's
search; 119 rows have no answering line). Raw predictions: `base_eval.json`. Runtime 785 s on the presentation Mac.

| Source | Rows | Exact match | Abstain recall | Abstain precision | Over-select | Under-select |
|---|---|---|---|---|---|---|
| All | 365 | 0.414 | **0.118** | 1.000 | 0.118 | 0.394 |
| SQuAD 2.0 | 150 | 0.407 | 0.100 | 1.000 | 0.133 | 0.100 |
| HotpotQA | 100 | 0.190 | 0.056 | 1.000 | 0.146 | 0.720 |
| LongMemEval | 100 | 0.580 | 0.000 | — | 0.095 | 0.337 |
| Demo fixtures | 15 | 0.867 | 0.667 | 1.000 | 0.000 | 0.000 |

The main weakness is abstention: when no line answers the question, the base model still cites one 88% of the
time. On the demo fixtures it passes all 9 answerable questions and fails 2 of the 6 near misses ("Saffron Bridge
launch party" with four lines shown, and "amber lighthouse party"). An earlier build of the same set with exactly
five lines per row gave abstain recall 0.076; fewer lines make abstaining easier.

Definitions: exact match = predicted citation set equals the gold set. Abstain recall = share of no-answer rows
where the model returned no citation; abstain precision = share of empty predictions that were correct.
Over-select = answerable rows with at least one wrong extra citation; under-select = answerable rows missing a
gold citation (HotpotQA needs two or three).

## Training plan

`kaggle/selector_train.ipynb` trains a QLoRA adapter (rank 16, all language-model attention, linear-attention
and MLP projections) on `train.jsonl` (3,000 rows, 35% empty targets) and scores base vs adapter on `dev.jsonl`.
The sealed set is never downloaded on Kaggle.

## Promotion gate (fixed before any adapter result exists)

The comparator is the **converted base**: unmodified HF Qwen3.5-4B taken through the same merge → GGUF →
quantize → `ollama create` route the adapter will use, scored with `scripts/eval_selector.py`. The official
nvfp4 `qwen3.5:4b` numbers above only describe today's app. The adapter, served the same way, is promoted only
if on the sealed set:

1. Abstain recall is at least **0.50** (base: 0.118).
2. Abstain precision is at least **0.85** (it must not refuse real questions to get there).
3. Exact match on answerable rows is no worse than the converted base minus 0.02.
4. All 9 answerable demo fixtures still pass, and at least 5 of the 6 near-miss fixtures return no citation.
5. No parse or request errors.

If it misses any item, the adapter stays an experiment and the app keeps the official model.

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
