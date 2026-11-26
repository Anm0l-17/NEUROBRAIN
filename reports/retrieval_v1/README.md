# Retrieval v1: stemming, stopwords, and the next note (26 Nov 2026)

`MemoryStore.search` is what feeds the citation selector its top five notes. Two book club questions failed
because the note that answers them never reached those five.

## What changed (`src/neurobrain/core.py`)

1. **Stemming.** The search index now uses SQLite's `porter unicode61` tokenizer, so "books" matches "book" and
   "picks" matches "pick". Existing databases are rebuilt automatically the first time the new code opens them.
   This takes under a second for a personal store. `user_version` stays at 1, so older app builds (for example the
   `demo-week-2026-11` checkout) can still open the file.
2. **Stopwords.** Question words ("who", "what", "is", "the", and so on) are dropped from the query. Before, they
   let unrelated lines such as the parking note fill the top five. If a query has nothing but stopwords, the
   original words are used.
3. **Next note.** For saved pages (observations), the top note's next note on the same page gets the last slot.
   Notes are pieces of one page, so the next one often finishes the thought without repeating its words: "The
   current book is no longer The Glass Orchard" is followed by "The group dropped it halfway through and switched
   to Salt and Signal". Plain file passages and `limit=1` searches are not affected. When there are fewer hits
   than the limit, the next note is added even if it shares no query word.

The `search()` contract is unchanged: same keys, citations as `source_id:chunk_id`, only active and allowed
sources, the same duplicate linking. `rank` is `NULL` for the next-note row, and nothing in `src` reads `rank`.
`answer()`'s recheck runs the same search, so a cited next note survives it (tested).

## Measurement

Fixed set: [`fixture.json`](fixture.json). It holds the retyped book club page with the 13 notes the windowed
extraction stored, the Saffron Bridge notes, and the 15 `source: fixture` questions from
`data/selector_v2/eval_sealed.jsonl` (amber, violet and Mira notes included). That makes 16 answerable questions
and 6 near misses.

Run it with:

```bash
NEUROBRAIN_SELECTOR_MODEL=neurobrain-selector-v2 PYTHONPATH=src .venv/bin/python reports/retrieval_v1/run.py --hybrid
```

| | Before ([before.json](before.json)) | After ([after.json](after.json)) |
|---|---|---|
| Answering note in top 5 (recall@5) | 14/16 | **16/16** |
| Same, with the encoder hybrid (`semantic.hybrid_search`) | 15/16 | 16/16 |
| v2 selector cites an answering note | 14/16 | **16/16** |
| Near misses with no evidence | 6/6 | **6/6** |
| Evidence lines shown to the selector (all 22 questions) | 103 | 75 |
| ...of which do not answer the question | 85 | 54 |

Fixed: "Who picks the books?" now cites "…handed book selection to Daniel". "What is the current book?" now cites
"…switched to Salt and Signal". No other answer changed. The selector runs at temperature 0, so each replay
gives the same answers.

### Which change fixes what (recall@5, no selector)

| Variant | Fixed set | Crowded set (+5 extra "book"/"current" notes) |
|---|---|---|
| stopwords only (no stemming) | 14/16; "Who picks the books?" returns **nothing** | not run |
| porter | 15/16 | 14/16 |
| porter + stopwords | 15/16 | 14/16 |
| porter + next note | 16/16 | 15/16 |
| porter + stopwords + next note (shipped) | 16/16 | 15/16 |

- Stopwords alone make things worse: "picks books" has no exact match, so the question gets zero evidence.
  Stopwords only make sense together with stemming. On this set they don't change recall, but they cut the junk
  lines by about a third (table above).
- No word-level option can fix "What is the current book?", because the answer shares no content word with the
  question. The encoder hybrid misses it too. The next-note rule is the only option tried that fixes it, and it
  keeps working when the store is crowded with other "current book" lines.
- **Known limit:** in the crowded set, "Who picks the books?" drops out again. Five other "book" lines outrank
  "handed book selection to Daniel" because "picks" never matches "selection". The encoder hybrid misses it too.
  Fixing that needs synonyms or a stronger encoder. That's out of scope here.

### Why not the encoder hybrid as the fix

It already exists (`semantic.hybrid_search`), but only the CLI and web `--semantic` paths use it. The chat app
(`chat_api` → `extract.answer`) calls `store.search`. The hybrid also needs torch and sentence-transformers at
runtime, and on its own it fixed only one of the two misses. The changes above reach every caller, including the
chat app, with no new dependency, and the hybrid still stacks on top of them (16/16).

## Still wrong (not retrieval)

"How much are the dues?" and "Who collects the dues?" score as correct because the old $5/Daniel line is one of
the accepted notes. The selector still cites the outdated line, even though the $8 and Aisha notes are now in
its top five. The selector never trained on updated facts. That's the knowledge-update gap noted in
`reports/selector_v2/README.md`.

## Follow-ups

- Hosted search in `cloud.py` (Postgres) has its own tokenizer and is unchanged.
- Synonyms ("picks" ↔ "selection") or a stronger encoder for crowded stores.
