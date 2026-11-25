# Citation selector v1 — baseline before training (25 Nov 2026)

Base `qwen3.5:4b` (Ollama, temperature 0, the app's exact request from `extract.selection_payload`) on the
sealed evaluation set `data/selector_v1/eval_sealed.jsonl` (365 rows; 118 have no answering line).
Raw predictions: `base_eval.json`. Runtime 922 s on the presentation Mac.

| Source | Rows | Exact match | Abstain recall | Abstain precision | Over-select | Under-select |
|---|---|---|---|---|---|---|
| All | 365 | 0.370 | **0.076** | 0.900 | 0.150 | 0.441 |
| SQuAD 2.0 | 150 | 0.367 | 0.067 | 0.857 | 0.167 | 0.133 |
| HotpotQA | 100 | 0.230 | 0.111 | 1.000 | 0.073 | 0.744 |
| LongMemEval | 100 | 0.470 | 0.000 | — | 0.219 | 0.417 |
| Demo fixtures | 15 | 0.667 | 0.167 | 1.000 | 0.000 | 0.000 |

The main weakness is abstention: when no line answers the question, the base model still cites one 92% of the
time. On the demo fixtures it fails exactly the near misses seen live — "Saffron Bridge launch party" (both
variants), "Who approved the budget?", "amber lighthouse party", "Where is the teal harbour review held?" —
and passes every answerable question and "pink submarine".

Definitions: exact match = predicted citation set equals the gold set. Abstain recall = share of no-answer rows
where the model returned no citation; abstain precision = share of empty predictions that were correct.
Over-select = answerable rows with at least one wrong extra citation; under-select = answerable rows missing a
gold citation (HotpotQA needs two or three).

## Training plan

`kaggle/selector_train.ipynb` trains a QLoRA adapter (rank 16, all language-model attention, linear-attention
and MLP projections) on `train.jsonl` (3,000 rows, 35% empty targets) and scores base vs adapter on `dev.jsonl`.
The sealed set is never downloaded on Kaggle. A promoted adapter must beat this table on the sealed set when
served through Ollama (merge → GGUF → `ollama create`), not only on Kaggle.

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
scorer. Our 48-row test set comes from one template family; treat these numbers as small-sample.
