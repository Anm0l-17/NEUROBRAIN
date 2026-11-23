# NeuroBrain Test accuracy and adaptive-chat check

Started 12 November and completed 13 November 2026, local time.

The installed `neurobrain-test` launcher defaults to adaptive (`auto`) mode. It makes a local rule-based decision with no classifier model call. Short factual questions, greetings and simple note lookups usually skip thinking. Calculations, analysis, programming tasks, large contexts, follow-ups and unknown requests use thinking. Only the final answer is displayed. `ollama run neurobrain-test` bypasses this launcher and does not provide adaptive routing.

## Reviewed results

| Mode | Checks passed | Median answer time | Total across 14 cases |
| --- | --- | --- | --- |
| fast | 11/14 | 0.95 s | 16.68 s |
| think | 12/14 | 35.50 s | 600.80 s |
| auto | 12/14 | 1.07 s | 211.93 s |

These are combined correctness, instruction-following and completed-generation checks on 14 authored development prompts, not a general factual-accuracy estimate. Fast/thinking requests were run once per case at temperature zero after a warm-up, alternating order. Adaptive scores and times reuse the identical selected request from each pair; the router adds negligible local work but these are not separately measured adaptive timings. Thinking used a 3,072-token total generation cap, fast used 768, and context was 8,192 tokens. The code rejects truncated outputs rather than presenting them as completed answers.

All final answers were read manually. The automated scorer initially passed a fast arithmetic answer because it included 660, but that answer also opened with an incorrect final price of 640. It was marked failed on review. The recorded JSON retains both the automated score and review note. Automated-only reruns require the same care.

## Failures and routing changes

- Fast and adaptive: the largest-country answer incorrectly says Canada instead of Russia. Thinking correctly says Russia. This known factual failure remains unresolved; routing does not repair missing or unreliable model knowledge.
- Fast and adaptive: the demo date and absent budget are factually correct, but the answer fails the explicit request to use the words “not stated.” This is an instruction-following failure, not an invented budget.
- Always-thinking: the simple demo-note question and the long room lookup both exhausted the generation cap after roughly 88–89 seconds without a completed answer.
- The initial adaptive selector unnecessarily sent the long room lookup through thinking. Length alone below the large-context threshold no longer triggers thinking. The original selector's raw results are preserved in `chat_accuracy_initial_router_2026_11_12.json`.
- Four follow-up prompts initially passed 3/4. “Access code” was mistaken for programming and exhausted the thinking cap. Programming cues were narrowed; that lookup then passed in 0.48 seconds. All four final follow-up responses are correct (Rome, R-42, 828 rupees, Mia), with the two reasoning cases taking 18.72 and 13.05 seconds. The failed attempt is retained. Because one case informed a fix, these are development checks, not held-out validation.

## Verification and limits

Eight focused unit tests cover routing, default auto mode, mode overrides, message validation, oversized output, hidden reasoning and generation truncation. Three existing interface regression tests passed. The installed launcher returned a brief greeting in a real default-mode smoke test. No full repository regression, dedicated lint run, repeated-sample study, adversarial suite, or broad benchmark was performed; a linter was unavailable. There was no training, commit or push.

The selector uses surface cues and can still misclassify short difficult questions or ordinary wording. Very large conversation contexts (over 6,000 characters) and non-greeting follow-ups conservatively enable thinking, so multi-turn sessions may be slower than fresh simple questions. Unknown personal facts remain unavailable unless supplied; this launcher does not retrieve or save memory. Use `--mode think` or `--mode fast` to override it. Thinking can still be slow or hit the cap on harder tasks.

Runtime: Ollama 0.40.16; local qwen3.5:4b-derived model; reported NVFP4 quantization and MLX runner. Actual model metadata is recorded in `chat_runtime_2026_11_12.json`. The server advertises only boolean thinking controls, with true as its default; adaptive behavior therefore lives in the launcher. Raw answers, prompts, timing and hashes are in `chat_accuracy_2026_11_12.json` and `chat_holdout_2026_11_13.json`.
