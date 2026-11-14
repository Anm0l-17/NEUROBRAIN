# Compact Qwen experiment on Kaggle

The reloaded Qwen3.5-4B adapter passed 8 of 9 development cases. The matched base passed 6 of 9. The required score was 9 of 9 plus improvement over baseline. The candidate fails the gate because it attributes a screenplay character’s vineyard to the user.

| Development case | Fresh base | Reloaded adapter |
|---|---|---|
| Unknown favorite TV series | Pass | Pass |
| Unspecified medication | Correct abstention, missing citation | Pass |
| Assistant-written hospital message | Wrongly says the user mentioned the hospital | Pass |
| Assistant-written observatory passage | Pass | Pass |
| Cousin moving to Kyoto | Pass | Pass |
| Direct user statement about wind turbines | Pass | Pass |
| User confirms tutoring job | Pass | Pass |
| User corrects partner’s occupation | Pass | Pass |
| Fictional vineyard owner | Wrong owner | Wrong owner |

Factual support and attribution passed on 7/9 base and 8/9 adapter answers. The E1 marker appeared on 8/9 and 9/9 respectively. Each model correctly abstained on the television and medication questions. Both accepted the explicitly confirmed job. The vineyard response contains a valid evidence ID but draws the opposite conclusion from the cited sentence. Neither model passed that case.

Kaggle completed 20 masked-target updates with seed 17, rank 8 LoRA and one Tesla T4. Peak allocated GPU memory was 10.64 GiB. Adapter weights occupied 3,674,248 bytes and were reloaded before generating the second set of answers. The completed training cell took 148.731 seconds including setup and both answer passes. Median per-answer generation times were 2.45 seconds for base and 1.74 seconds for adapter. Different answer lengths and baseline-first warm-up prevent a throughput claim. The exact revision, package versions, per-answer times and losses are in run_details.json. observed_answers.json contains both complete answer sets.

Training used 13 public-source adaptations across 12 personas. The nine reused development prompts include six fictional scenarios and three earlier PersonaMem adaptations. The benchmark and admission rows were excluded. Only supplied evidence was tested. Forget requests appear in training and have no independently scored case in this nine-prompt suite. No held-out quality, deletion, real-note accuracy, ordinary-chat, long-history or end-to-end retrieval result follows. Earlier MLX pilot scores came from a different runtime. The paired Kaggle base is the comparator for this run.

CodeRabbit reviewed an isolated copy of run.py and raised one issue: the standalone script depended on two notebook-defined hashes. The submitted Kaggle cell supplied both. The local standalone and self-contained notebook now embed the same frozen hashes. The weights were trained before this packaging fix.
