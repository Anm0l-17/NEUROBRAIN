# NeuroBrain Test adaptive chat

With Ollama running, from the project directory:

```sh
ollama create neurobrain-test -f ollama/Modelfile
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/neurobrain-test
```

The launcher defaults to `--mode auto`: short factual questions, greetings and simple note lookups skip thinking; calculations, analysis, code, large conversation contexts (over 6,000 characters), follow-ups and unrecognized requests enable it. A long but straightforward note lookup can stay on the fast path. Only the final answer is displayed. This is a conservative rule-based selector, not a learned difficulty estimator. It can misclassify short difficult questions. Prompt wording and conversation context affect routing.

Use `--mode fast` or `--mode think` to override the selector for the session. A quoted prompt can be supplied as an argument for a single answer. `/bye` exits interactive chat. History stays in this process; it is not saved to the memory store. Oversized chats are rejected rather than silently losing earlier context. Model errors and incomplete answers are reported.

`ollama run neurobrain-test` bypasses the launcher and therefore does not provide adaptive routing. Ollama exposes thinking per request; the model tag alone cannot run this Python selector. For direct CLI use, `--think=false` disables thinking and `/set nothink` disables it in an existing session. `--hidethinking` only hides the trace. API callers should set `think` explicitly. The evidence selector in `src/neurobrain/extract.py` already uses `think=False`; this chat launcher does not change that evidence-only service.

## Evaluation

The model now allows 8,192 generated tokens with a 16,384-token context window. The terminal launcher allows 2,048 generated tokens in fast mode and 8,192 with thinking, with a ten-minute request timeout. These are ceilings, not target answer lengths. Thinking can consume generation tokens. The original 1,024-token model cap was too small for long, multi-part tests. Larger limits can increase latency and context memory use; they cannot guarantee completion for arbitrarily large requests.

In Open WebUI, check the model's Advanced Parameters and the current chat's overrides: clear a saved Max Tokens / `num_predict` limit to inherit the model default, or explicitly set it to 8,192. Set the context size / `num_ctx` to 16,384 if overridden, save, and start a fresh chat. Display settings for reasoning do not change the generation budget. The terminal launcher reports incomplete generation as an error; direct Open WebUI chats do not use that check. Earlier evaluation reports describe the smaller limits used at that time, not these new settings.

```sh
PYTHONPATH=src python -m unittest discover -s tests -p test_chat.py -v
PYTHONPATH=src python scripts/evaluate_chat.py
```

The 14-case authored development smoke set covers greetings, geography, science, note extraction, missing information, quoted instruction injection, arithmetic, ordering, code, logic and long input. Expected answers and automated scoring patterns are in `tests/fixtures/chat_accuracy.json`. Read the recorded answers as well as the scores: pattern matching is not a semantic accuracy judge.

The evaluator warms the model, alternates fast/thinking order between cases, records elapsed answer time, and rejects generation-limit truncation. Adaptive results reuse the selected identical fast/thinking request, so their latencies are estimates from those paired runs, not a separate end-to-end benchmark. This small, single-sample set does not establish general accuracy or prove that thinking is always better. A faster response can still be factually wrong.

The router was refined using this development set after a long, simple lookup unnecessarily hit the thinking limit. Four follow-up prompts in `tests/fixtures/chat_holdout.json` were evaluated in actual auto mode. One exposed an access-code routing error, which was fixed and retested; the original failed attempt is preserved. Results are in `reports/chat_holdout_2026_11_13.json`. Despite the historical filenames, this set was used for refinement and is not held-out validation. The curated, manually reviewed report is `reports/Chat_Accuracy_2026_11_13.md`; rerunning the evaluator writes automated-only results to `reports/chat_accuracy_latest.json`, which need manual review for contradictions.
