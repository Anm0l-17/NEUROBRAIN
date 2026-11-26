# Extraction recall v1: why two book club facts were dropped (26 Nov 2026)

"Priya Raman founded it in 2023…" and "Rosa … gives members 10% off drinks" were never stored.
Model: Ollama `qwen3.5:4b`. All pages are fictional.

## Causes

Not the window cut, the dedupe step or the vague-quote filter. All three causes are in what the model returns:

| Cause | Seen as | Fix in `extract.py` |
|---|---|---|
| The page was sent as ASCII JSON, so "Café" arrived as `Café`. The model quoted it back as "Cafè" | Rosa quote failed the exact match | Send the text unescaped (`ensure_ascii=False`), extraction only |
| The model rewrote quotes ("Rosa reserves…" without the commas) | Failed the exact match | Prompt: copy character for character |
| The model skipped sentences, sometimes stopping after the first | "founded" sentence never returned | Prompt: check every sentence. Then **one more call per window** with only the sentences that no quote covers |

The exact-quote check and `import_observation`'s re-verification are unchanged: a second-pass quote must match
the original text like any other. The selector request (`selection_payload`) is unchanged, because v2 was
trained on that format.

## Locked test pages (the unbiased number)

[`testset.json`](testset.json): four pages with chatter, pronoun-only and vague lines, written before any variant
ran on them. One run per variant, nothing changed afterwards. A fact counts when one stored note contains its key.

| Variant | Facts kept (46) | Time | Raw |
|---|---|---|---|
| Old code | 39 | 27 s | [test_old.json](test_old.json) |
| Unescaped input only | 45 | 27 s | [test_utf8.json](test_utf8.json) |
| Unescaped input + prompt | 43 | 28 s | [test_prompt.json](test_prompt.json) |
| **Shipped:** unescaped + prompt + second pass | **45** | 35 s | [test_prompt_retry.json](test_prompt_retry.json) |

Read this honestly: on unseen pages, nearly all the gain comes from the one-line encoding fix. The prompt and
second pass tie with it and cost about 30% more time. They are shipped because the encoding fix alone still
dropped the Rosa sentence on the book club page, which was the bug to fix. No chatter or vague line was
stored by any variant.

## Development pages (these shaped the fix, so they overstate it)

Seven pages: book club, Saffron Bridge, and [`dev_pages.json`](dev_pages.json). The first three dev pages and both
fixture pages were used to choose the prompt; the second pass was designed after the "clinic" page failed.

| Variant | Facts kept (79) | Book club (20) | Raw |
|---|---|---|---|
| Old code | 70 (65 to 71 across four runs; the first file was overwritten) | 17 (15 in the five-page run, `dev_runs/5pages_old.json`) | [before.json](before.json), `dev_runs/7pages_old_run*.json` |
| Prompt, no second pass | 70 | 20 | [dev_runs/7pages_prompt_no_retry.json](dev_runs/7pages_prompt_no_retry.json) |
| Shipped | 79 (both runs) | 20 | [after.json](after.json) |

The prompt without the second pass kept only 3 of 10 clinic facts (old code: 9), because the model stopped
partway. That is why the second pass exists. Earlier five-page prompt comparisons are in `dev_runs/5pages_*.json`;
"cover rule only" lost 3 of 7 Saffron Bridge notes and was rejected.

**Run-to-run noise:** at temperature 0 the extraction model still varies between runs on this Mac, so a gap of a
few facts between two single runs is not meaningful.

## Live check on a scratch copy of the live database

Same retyped page text in both columns, saved under the live page's key (`reimport_book_club.py`), then the
unchanged `reports/live_check/score.py`. The untouched copy reproduces the 26 Nov result (v2 15/20, base 12/20).

| | Old extraction | New extraction | New, repeat |
|---|---|---|---|
| `neurobrain-selector-v2` | 14/20 | **17/20** | 17/20 |
| `qwen3.5:4b` | 11/20 | 14/20 | 13/20 |
| "Who founded the club?" (v2) | no answer | correct | not run |
| "What discount do members get at the café?" (v2) | no answer | correct | not run |

Raw: `live_check_{untouched,a_old,b_new,b_new_repeat}.json`, `extra_{a_old,b_new}.json`, `live_notes_{old,new}.json`.

- v2 got no question worse. It gained "Which Thursday", "Which chapter" and "Why did the venue change?", because
  the stored note is now the whole sentence, including the cause.
- v2 still misses both dues questions (it cites the old $5 line; this is the v3 target) and "library room fee".
- Base Qwen got one trick question worse ("discount at the library" now cites a dues line). Base is not the
  live selector.
- The repeat was a second extraction that produced the same 14 notes (`live_notes_new_repeat.json`).

## Demo fixtures F01–F11

Old and new code both pass all eleven ([old](f01_f11_old.json), [new](f01_f11_new.json)). F06 ("Okay, thanks.")
and F07 ("Move that to there…") store nothing, although the second pass now asks about them again. Notion and OCR
are simulated in this harness. F12 and F13 need hosted Supabase and were not run.

## Limits

- Up to one extra model call per window. Total time rose by 30% on the locked pages and about 6% on the development pages. Screen watch mode
  re-extracts on every change. The 5-second source-to-saved target was already missed for long pages.
- Extra notes past 12 per window are cut. If the second call fails or returns a malformed item, the save fails as a first-call failure does, and the earlier version stays. That gives each page one more chance to fail.
- A second-pass sentence is sent without its neighbours, so a stored note can start with "He" or "It".
- `reports/retrieval_v1/run.py` uses notes written into its fixture, so it cannot see extraction changes.

## Re-run

```bash
PYTHONPATH=src python3 reports/extraction_recall_v1/run.py --set test
```
