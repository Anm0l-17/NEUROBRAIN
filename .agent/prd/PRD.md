# NeuroBrain semantic retrieval experiment

## Objective

Measure whether a local MiniLM embedding index improves retrieval for paraphrased fictional-note questions while preserving the existing lexical baseline, citations, policy filtering, and deletion behavior.

## Constraints

- Keep the current SQLite/FTS5 lexical path working.
- Use the pinned local `sentence-transformers/all-MiniLM-L6-v2` revision from the training lock.
- No network access, cloud storage, model fine-tuning, or generated answers.
- Do not claim semantic improvement until the paired evaluation reports it.

## Acceptance criteria

1. The semantic experiment runs from a clean checkout with cached model assets.
2. Embeddings have the expected dimension and finite values.
3. Retrieval results retain source IDs, chunk spans, and citations.
4. Deleted sources do not appear in semantic results after restart.
5. The report compares lexical and semantic Recall@K on the same fictional cases.
6. Model-unavailable behavior is an explicit lexical fallback, not silent data loss.


## Overnight prototype continuation — 13 November 2026

User authorized multiple sequential implement/test/review sessions, with morning review. Preserve previous work. Prioritize local model runtime diagnosis, reproducible fictional end-to-end demo, safe observation behavior, integration preparation and presentation materials. Live account/OS acceptance remains explicit. No deployment or push. Each session records changed files, tests, review status and unresolved gates. Do not export datasets or reports to review services without permission.


## Generator pilot authorized 13 November 2026
User requested a small theoretical PersonaMem-v2 pilot, review, then conditional expansion. TASK-006 covers isolated Qwen3.5-4B QLoRA training and development comparison. Preserve benchmark holdouts and current runtime; no production promotion from a pipeline smoke test.


## Attribution repair, 13 November 2026
TASK-007: small pilot only, 17 training and 9 development examples. Same base/settings as v0, fresh adapter. Retest against baseline and previous adapter. User explicitly prohibits scaling; leave production unchanged regardless of outcome.

## Compact Kaggle experiment, 14 November 2026

TASK-008 covers the ten-source shortlist and matched Qwen development comparison on anm0l17/gpu-server. The user approved transfer of 13 generator training and nine development examples. Admission IDs stay separate. See data/neurobrain_shortlist_v1/SOURCES.md for the selection and decision rule.
