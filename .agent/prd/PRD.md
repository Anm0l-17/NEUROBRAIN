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
