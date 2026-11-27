# Live prototype check

`score.py` asks the app's own `answer()` 20 questions on a copy of the live database (14 book club notes from the
Notion page plus the amber lighthouse note), once per selector model. It writes JSON with every cited line.
It is a spot check written after seeing the stored notes; the sealed gates in `reports/selector_v2` and
`reports/selector_v3` remain the unbiased scores. Re-run it unchanged after any model or search change.

## 26 Nov 2026 (commit `401bac5` code, raw `2026-11-26.json`; two runs, identical)

| Model | Answerable (13) | Half-right (old + new line) | Trick questions refused (7) | Total |
|---|---|---|---|---|
| `qwen3.5:4b` | 7 | 3 | 5 | 12/20 |
| `neurobrain-selector-v2` | 9 | 0 | 6 | 15/20 |

v2 misses:

| Question | v2 cited | Cause |
|---|---|---|
| How much are the dues? | the $5 line | Selector chose the outdated line; the $8 line was in the top five (v3 target) |
| Who collects the dues? | the $5 / Daniel line | Same; the Aisha line was in the top five (v3 target) |
| Which Thursday does the book club meet on? | "first Thursday" | Same; "second Thursday" was in the top five (v3 target) |
| Why did the book club venue change? | nothing | Search: "Corner Grind closed for renovation" was not in the top five |
| How much is the library room fee? | the $8 dues line | The page never states the fee (arguably acceptable) |

Extraction kept 14 of about 16 page facts; "Priya Raman founded it in 2023" and Rosa's 10% discount were not stored,
so they are not asked here.

## 27 Nov 2026: selector v3

`score.py` unchanged, three selectors, two databases. Each cell was run twice with identical citations. Base Qwen
can differ slightly between runs on other days.

- **Stored notes:** a fresh read-only backup of the live database (page version 5, same as 26 Nov).
  Raw: [`2026-11-27.json`](2026-11-27.json), `2026-11-27-repeat.json`.
- **Re-extracted notes:** the same copy with the book club page replaced by the new extraction of its retyped text
  ([`extraction_recall_v1`](../extraction_recall_v1/README.md)). Raw: [`2026-11-27-reextracted.json`](2026-11-27-reextracted.json),
  `2026-11-27-reextracted-repeat.json`.

| Selector | Stored notes | Half-right | Re-extracted notes | Half-right |
|---|---|---|---|---|
| `qwen3.5:4b` | 12/20 | 3 | 14/20 | 2 |
| `neurobrain-selector-v2` (app default) | 15/20 | 0 | 17/20 | 0 |
| `neurobrain-selector-v3` | 17/20 | 0 | 17/20 | 0 |

| v3 miss | Stored notes | Re-extracted notes |
|---|---|---|
| Who collects the dues? | cites the old $5 line | cites the old $5 line |
| How much is the library room fee? | cites the $8 line | cites the Aisha and $8 line |
| Why did the book club venue change? | nothing (line not retrieved) | correct |
| Which chapter should we read up to? | correct | **cites the old "chapter 18" line** (v2 is correct here) |

v3 gains "How much are the dues?" on both databases and "Which Thursday" on the stored notes. On the re-extracted
notes it ties v2: it fixes the dues amount and loses the chapter question. v3 is not the app default because it
failed [its sealed gate](../selector_v3/README.md). The v3 book club fixtures use the older, shorter note wording, so
they and the right-hand column are not the same test.

