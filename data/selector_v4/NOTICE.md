# Licence and attribution

The rows in this folder are derived works:

- **SQuAD 2.0** — Rajpurkar, Jia and Liang (2018), https://rajpurkar.github.io/SQuAD-explorer/, via `rajpurkar/squad_v2`. CC BY-SA 4.0.
- **HotpotQA** (distractor setting) — Yang et al. (2018), https://hotpotqa.github.io/, via `hotpotqa/hotpot_qa`. CC BY-SA 4.0.
- **LongMemEval** (oracle file; single-session/multi-session questions in train and dev, knowledge-update questions in train, dev and the sealed update file, split by question) — Wu et al. (2025), https://github.com/xiaowu0162/LongMemEval, via `xiaowu0162/longmemeval-cleaned`. MIT.
- Update templates (`update_*` rows) — fictional text written for this project.
- Demo and book-club fixtures — fictional notes written for this project, evaluation only.

LoCoMo (CC BY-NC) is not used. Sentences were split, selected and shuffled, and citation IDs were added. Because of the SQuAD and HotpotQA share-alike terms, `train.jsonl`, `dev.jsonl`, `eval_sealed.jsonl` and `eval_update_sealed.jsonl` are distributed under **CC BY-SA 4.0** (https://creativecommons.org/licenses/by-sa/4.0/). Exact sources and hashes are in `manifest.json`.

v4 adds `teacher_*` rows (`teacher_rows.jsonl`): fictional notes written and labelled for this project by Claude Sonnet 5.5 (teacher), with labels confirmed by a second, blind Sonnet pass. v4 contains no sealed file; v4 is scored on `data/selector_v3/eval_sealed.jsonl` and `eval_update_sealed.jsonl`, unchanged.
