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
