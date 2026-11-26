# Hybrid retrieval in the chat answer path: off by default (26 Nov 2026)

`NEUROBRAIN_HYBRID=1` makes the chat app pick its five notes with `semantic.hybrid_search` (word search plus
the local MiniLM encoder, merged by reciprocal rank fusion) instead of word search alone.
**It is not better, so it stays off.**

## What changed

- `extract.search_evidence` is the one retrieval used by all three places that search for an answer: the first
  search in `answer()`, its recheck, and the final recheck in `chat_api` before the reply is sent. If any one of
  them used word search, a note found only by the encoder would be dropped, or the chat app would reply
  "Evidence changed; ask again." `tests/test_hybrid.py` fails if either recheck is reverted.
- Without the local encoder, it falls back to word search. Hosted memory always uses its own search.
- A note saved through two routes now takes one of the five slots, not two.
- The index is marked with the database state read *before* the notes, so a save made during a rebuild is not
  missed.

## Measurement

Selector `neurobrain-selector-v2`. "Old notes" is an untouched copy of the live database; "new notes" is the same
copy with the book club page re-extracted by the new code (`reports/extraction_recall_v1`).

| | Word search | Hybrid |
|---|---|---|
| Retrieval fixture: answering note in top 5 | 16/16 | 16/16 |
| Retrieval fixture: selector correct, near misses refused | 16/16, 6/6 | 16/16, 6/6 |
| Live check, old notes (v2) | 15/20 | 15/20 |
| Live check, new notes (v2) | **17/20** | **15/20** |
| "Why did the venue change?", old notes | no answer | **wrong answer** (the school-event line) |
| "Why did the venue change?", new notes | correct | correct |

Raw: `retrieval_recall.json` (top-5 row), `retrieval_{off,on}.json`, `live_check_{untouched,b_new}_{off,on}.json`,
`extra_{untouched,b_new}_{off,on}.json`. Base Qwen is in the live check files too; it is not the live selector.

The two new-notes losses:

- "What is the current book?": the merge pushes the page's next note ("…switched to Salt and Signal") out of the
  top five, so the selector refuses.
- "Which Thursday…?": the merge reorders the notes and the selector cites the outdated "first Thursday" line.

On the old notes, the "closed for renovation" line is still not in the hybrid's top five. The question that
motivated this experiment is answered by the extraction fix instead, because the stored note now holds the whole
sentence, cause included.

## Cost when switched on ([startup.jsonl](startup.jsonl), three fresh processes, 41 notes)

| | |
|---|---|
| Loading torch and the encoder (paid by the first question) | 2.6 to 4.0 s |
| First search, building the index | 0.03 to 0.14 s |
| Later searches | 3 to 4 ms |
| Peak memory of the process | about 26 MB → 480 to 512 MB |
| Sees a note saved by another process | yes |

With the flag off, torch is never imported, so start-up is unchanged. During the measurement, one hybrid live-check
run took about 9 minutes instead of about 70 s while the Mac was deep in swap; the cause was not established.

## Limits

The encoder search has no relevance cut-off, so with the flag on every question reaches the selector with five
notes, and refusing unrelated questions depends on the selector alone.
