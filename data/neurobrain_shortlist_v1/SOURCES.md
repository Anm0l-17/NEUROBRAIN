# Compact shortlist, 14 November 2026

| Source | Selection for this experiment |
|---|---|
| NeuroBrain reviewed exploratory admission corpus | 200 existing reviewed training IDs, 100 keep and 100 skip across 75 fictional scenario groups. The frozen source hash matches. All 200 have known reviewed actions. Zero normalized candidate-text matches with the original admission pilot. Shared templates still limit independence. Keep explicit privacy overrides, uncertain labels, validation thresholds and suggestion mode. |
| PersonaMem-v2 | Qwen training only. Six starter examples plus seven new evidence-grounded adaptations. Pinned text training CSV and CC BY 4.0 attribution in manifest.json. Use generator_compact.jsonl and compact_manifest.json together. |
| Multi-Session Chat (MSC) | Excluded. The official project page documents release and access, but supplies no explicit dataset-specific license. https://parl.ai/projects/msc/ |
| DialogSum | Optional supplement deferred. Dialogue summaries supply no reviewed NeuroBrain keep/skip labels. |
| PersonaMem-v3 | Evaluation only. Restrict events to those preceding each query. Keep scorer preferences and answers out of model input. |
| LifeDialBench | Evaluation only. Shared viewpoints and same-day timestamps complicate temporal splits. Resolve before scoring. |
| MemoryAgentBench | Evaluation only. Track upstream LongMemEval overlap and shared contexts. Oversized histories require retrieval. |
| PerLTQA | Evaluation only. Use updated English v2 and group linked characters. Record missing memories separately. |
| LongMemEval-S | Evaluation only. Group overlapping histories, reserve final questions and keep evidence labels scorer-side. |
| LoCoMo | Evaluation only. Partition by complete conversation and keep gold answers and evidence IDs scorer-side. |

## What was read

The six starter training inputs and targets were reviewed directly. For the new sample, the full 18,549-row text training index was scanned for eligibility. Excluding validation, benchmark and prior pilot personas and requiring the source sensitivity flag to equal False left 1,307 rows. From each file-order decile, one dialogue with a serialized snippet under 1,900 characters was selected with Python Random(17). GPT-6 read all ten selected snippets. The short-dialogue cap and one draw per decile limit coverage of longer histories, persona diversity and rare topics. The 1,307 figure counts structural eligibility only.

Seven new adaptations cover a forgotten book genre, historical society recommendations, assistant-written Lyon narrative, panelist and audience attribution, unconfirmed lunch invitation, withdrawn rooftop preference, and assistant-written courtyard photography. Three rejected snippets are recorded by row and reason in compact_manifest.json. Question and target were authored from the supplied turns. User-submitted writing is attributed to its writer, and an instruction to forget overrides earlier suggestions. Training tests abstention and instruction following, not physical deletion of model weights.

All 13 personas/row selections were checked against upstream validation and benchmark persona IDs and the prior v0 persona manifest, which also covers the external examples inherited by v1. Multiple rows can share one training persona. Neither prior pilot's train/development/test files yielded an identical normalized evidence prefix. The v1 test file is a development alias. Benchmark answers were not used. This audit does not establish independence from Qwen pretraining or detect every paraphrase.

## Decision rule fixed before the run

Use the nine prior development prompts, greedy decoding, thinking disabled, and 180 generated tokens per answer for both models. Check factual support, speaker attribution, appropriate abstention or positive confirmation, coherent output and E1 citation. Require all nine combined passes and improvement over the matched base. Keep development latency separate from retrieval and deployment performance. No final benchmark or real-user evaluation is part of this run.

Two selected admission IDs also appeared in the separate 16-row admission-start training smoke test: batch-a-00-01, batch-a-00-10. They remain training examples.

A separate semantic spot check read the first and last selected record per action in source order for each of admission batches A, B and C (12 of 200). A's durable crate-reuse rule and recurring sensor fault support keep; moving a crate and acknowledging a diagram support skip. B adds a route preference and identifies the cousin holding originals; both skips repeat the supplied history. C adds an availability constraint and a recordkeeping decision; both skips repeat already confirmed room/menu facts. Existing labels were retained. This was a check of the prior labels, not a second human adjudication.

## Attribution final evaluation set, rewritten 16 November 2026 (frozen before any training)

`attribution_final_eval.jsonl` was rewritten before the candidate run because its six rows copied the training and development templates (same stems, same fictional objects), and row 4 asked where the user lives when the evidence only said the user rents a cabin. The previous file (SHA-256 `52b2838ef8f0b81501099ce33778e3077675f5cc25399b794bffba23f6d69220`, commit `70a378b`) is superseded and must not be used for scoring.

**New file SHA-256: `89d1c48bc69950339d974eafc349e8a6228cfe7f1361d7e75c26a0cc33677185`.** Record the hash again in the training notebook and the results file; if it differs, the set was edited after freezing and the comparison is invalid.

Six rows, all fictional, one system prompt identical to `attribution_hard_train.jsonl`: forwarded message from a third party (not a user fact); a plain direct statement with a differently phrased question; screenplay character working hours (abstain); the user also stating the same fact (confirm); a withdrawn menu preference; and a cancelled reminder that must not remove an unrelated stated fact. The question always matches the relation in the evidence. Checked mechanically: no normalized evidence text matches any row of `attribution_hard_train.jsonl`, `attribution_followup_dev.jsonl`, `generator_train.jsonl` or `generator_compact.jsonl`. This does not detect paraphrases or pretraining exposure. Open the set once, after the candidate is chosen on the development cases; do not train on it or tune a prompt against it.
