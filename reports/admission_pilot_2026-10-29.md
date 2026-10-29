# NeuroBrain fictional training pilot — 29 October 2026

## Outcome

**The first small training trial completed successfully. The neural model is not ready
for automatic memory exclusion. A simpler baseline performed better on this fixture.**

No Qwen weights were changed. No private notes were read or used for training. The
running application is unchanged: this experiment cannot reject imported memories.

## What was trained

- Randomly initialized memory-admission MLP: 388 → 128 → 32 → 1; **53,953 trainable parameters**.
- Frozen sentence-transformers/all-MiniLM-L6-v2 encoder, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Inputs: normalized 384-dimensional embedding plus capped log word count, Markdown heading,
  list-item indicator and maximum cosine similarity to earlier candidates in the same scenario.
- Chronological features do not use future records or labels. Cold-start similarity is zero.
- CPU, float32, seed 17; AdamW learning rate 0.001, weight decay 0.0001,
  batch size 32, dropout 0.2, BCEWithLogitsLoss, maximum 30 epochs, early-stopping patience 5.
- Best validation-loss epoch: **30**. Best weights and optimizer state saved.
- Training loss: 0.6982 → 0.3678.
- Candidate-first context composition is capped at 256 wordpieces; 0 inputs truncated.
  Word-count normalization is fixed, not fitted on validation/test. No other fitted scaler.

## Data and partition

80 fictional examples: 16 scenario families, five candidates per family; 48 useful and
32 not useful. Labels and rationales were authored by the same assistant that built the
pipeline and remain **pending human review**. This is not independently established gold data.

| Split | Scenario families | Records | Useful | Not useful |
|---|---:|---:|---:|---:|
| Training | 10 | 50 | 30 | 20 |
| Validation | 3 | 15 | 9 | 6 |
| Held-out test | 3 | 15 | 9 | 6 |

Scenario and declared family IDs never cross splits. Exact normalized duplicate
candidates are rejected. This does not establish absence of near-duplicate patterns.
This deliberately small 10/3/3 family split is a trial deviation from the eventual
70/15/15 plan. No public benchmark or Kaggle examples were downloaded for this run.

Dataset SHA-256: `f276358074504f4ca76167d34c5162e597b42c83f294384a104894c995e5fa2a`.

## Results on 15 held-out fictional records

| Method | Precision | Useful-memory recall | F1 | Useful items missed | Unhelpful items kept |
|---|---:|---:|---:|---:|---:|
| Neural MLP | 100.0% | 77.8% | 0.875 | 2 | 0 |
| store_all | 60.0% | 100.0% | 0.750 | 0 | 6 |
| majority | 60.0% | 100.0% | 0.750 | 0 | 6 |
| rules | 100.0% | 22.2% | 0.364 | 7 | 0 |
| tfidf_logistic | 75.0% | 100.0% | 0.857 | 0 | 3 |
| embedding_logistic | 90.0% | 100.0% | 0.947 | 0 | 1 |

Precision means the share of suggested stored items labeled useful. Recall means the
share of all useful items retained. These percentages have very small denominators:
one missed useful item changes recall by 11.1 percentage points.

The neural threshold was **0.474605**, selected on validation only
by maximizing precision subject to at least 95% validation recall. Validation retained
9/9 useful items and 3/6 unhelpful items (75% precision). At that same frozen threshold,
test retained 7/9 useful items and 0/6 unhelpful items. **Validation success did not carry
over to test; test recall of 77.8% fails the plan's 95% recall target.**

The embedding logistic baseline uses the same 388 features. TF-IDF vocabulary was fit
on training only. Logistic thresholds were chosen on validation; majority prediction
uses training labels only. The simple keyword rule was defined before test inspection.
No architecture or threshold was changed after inspecting test results.

The 60%-positive fixture makes majority prediction equivalent to store-all. Neither
baseline should be mistaken for a learned memory decision model.

## Two useful records missed by the neural model

1. “The left motor reverses direction whenever the controller reboots.”
2. “The wheel encoder produces 360 pulses per revolution.”

Both are in the held-out robotics scenario. This suggests a weakness worth investigating
with new data, but two misses cannot establish its cause. Do not tune to these exact
sentences and then present the same test as independent evidence.

## Verification

- A fresh Python process loaded the trusted local checkpoint with `weights_only=True`.
  Predictions matched all 80 saved scores exactly: maximum absolute error **0.0**
  (allowed tolerance 0.000001). This checks checkpoint reload on saved features;
  it does not independently validate all feature preprocessing.
- Five new data-safety tests cover draft-label refusal, cross-split scenario leakage,
  cross-split family leakage, duplicate text and inappropriate provenance.
- Lint and formatting checks passed for source, scripts and tests.
- Full test discovery: 19 passed; one existing HTTP test could not open a loopback
  socket under current execution restrictions. It raised PermissionError, so this is
  an unavailable environment check, not a confirmed HTTP regression or a passing test.
  Source-path non-HTTP tests were separately rerun; see verification output.

## What these results do not establish

No claim of real-user generalization, better downstream answers, privacy detection,
calibrated probabilities, realistic storage savings, GPU performance or production
readiness is justified. This is one configuration and one seed, not the planned
three-seed comparison or ablation study. No bootstrap confidence intervals were computed.
Markdown/list indicator features are zero in this fixture and therefore untested.
The examples contain easy stylistic cues and omit many hard negatives, evolving contexts,
privacy checks, ambiguous labels, corrections across sessions and realistic class skew.
Neither assistant-authored evaluation labels nor a tiny clean split resolves those limits.

## Files and reproduction

- Data: `data/admission_pilot_v0.jsonl`; dataset notes: `data/README.md`.
- Training: `scripts/train_admission.py`; reload verifier: `scripts/verify_admission_checkpoint.py`.
- Installed versions: `requirements-training.lock.txt` (macOS arm64, Python 3.13.1).
- Run directory: `models/admission-pilot-v0-seed17/` contains checkpoint.pt,
  report.json, predictions.jsonl, reload_fixture.npz and reload_check.json.
- Machine-readable results copied to `reports/admission_pilot_2026-10-29.json`.

From the project root, after installing the optional training dependencies:

```bash
HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false .venv/bin/python scripts/train_admission.py --allow-draft --output models/admission-pilot-v0-reproduction
HF_HUB_OFFLINE=1 .venv/bin/python scripts/verify_admission_checkpoint.py models/admission-pilot-v0-reproduction
PYTHONPATH=src HF_HUB_OFFLINE=1 .venv/bin/python -m unittest discover -s tests -v
```

The output path must be new; existing experiments are never overwritten. MiniLM must
already be cached at the pinned revision; offline mode fails rather than substituting
another encoder or synthetic embeddings. Training dependencies are separate from the
application's standard-library runtime. Qwen/Ollama is not required by this experiment.

## Next work when you return

Review the 80 draft labels and refine the usefulness rubric, particularly technical
facts and unresolved faults. Create a larger, harder, independently reviewed dataset
with fresh held-out families. Compare the MLP against embedding logistic regression;
keep the simpler baseline as a serious candidate. Run the planned seeds and ablations
only after the dataset is ready. Keep admission suggestion-only until recall and
end-to-end answer-quality gates pass. Do not change the app to discard notes based on
this checkpoint.

## Method references

- Project specification: `docs/NeuroBrain_Session_Plan.md`, sections 4–5.
- [PyTorch optimization tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html).
- [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).

## Delivery self-check

The requested small fictional experiment and reviewable report are complete.

| Axis | Score | Evidence and remaining improvement |
|---|---:|---|
| Accuracy | 4/5 | Counts come from executed predictions; labels remain assistant drafts, so human review is still needed. |
| Completeness | 4/5 | Training, five baselines, checkpoint reload and report completed; existing HTTP test unavailable under execution restrictions. |
| Clarity | 4/5 | Misses and failed recall target are explicit; the detailed report is longer than the return summary. |
| Actionability | 4/5 | Data, weights, scripts, lockfile and reproduction commands saved; meaningful model selection needs reviewed data. |
| Conciseness | 4/5 | Short return summary links to detailed evidence; report repeats some limitations for clarity. |

Overall: 4.0/5. Highest-impact follow-ups: independent label review, harder fresh test
families, and three-seed comparison once the data is ready. Self-check: the user can
inspect the run later without granting permissions and can distinguish a pipeline
success from a model ready for use.
