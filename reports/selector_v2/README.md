# Citation selector v2 — data and gate before training (25 Nov 2026)

Adapter v1 failed its gate by over-abstaining (`reports/selector_v1/README.md`): its SQuAD training rows were
52% empty and it never trained on conversation-style evidence. `data/selector_v2` (built by
`scripts/build_selector_data.py`, data commit `8496da4`) changes only the data; the notebook settings are unchanged
(seed 17, lr 2e-4, rank 16, accumulation 8, one epoch).

| Split | Rows | Empty | SQuAD 2.0 | HotpotQA | LongMemEval | Fixtures |
|---|---|---|---|---|---|---|
| Train | 2,808 | 20.0% | 1,150 (22% empty) | 1,400 | 258 (86 questions × 3 renders) | — |
| Dev | 323 | 40.9% | 150 | 144 | 29 | — |
| Sealed | 291 | 37.8% | 150 (60 answerable) | 96 | 30 (28 answerable) | 15 (same rows as v1) |

LongMemEval uses only single-session-user and multi-session questions (temporal-reasoning answers need session
dates the turns do not show; knowledge-update marks old and new values alike). The v1 sealed set is **retired**:
no v2 sealed row (fixtures aside) shares a question or evidence line with it, and its LongMemEval questions, never
trained on, now sit in train and dev. Few unseen LongMemEval questions remained, so the sealed LongMemEval slice is
30 rows (v1: 100); treat its per-source numbers as small-sample.

## Comparator on the v2 sealed set

`neurobrain-selector-base` (converted base, same route as any adapter), raw `converted_base_eval.json`, 948 s:

| Exact match | Answerable exact | Abstain recall | Abstain precision | Over-select | Errors |
|---|---|---|---|---|---|
| 0.433 | 0.530 (96/181) | 0.273 | 1.000 | 0.050 | 0 |

Fixtures: 9/9 answerable pass; near misses 4/6 (fails "Saffron Bridge launch party" with five lines and
"amber lighthouse party", as on v1).

Reference only (not a comparator): adapter v1 (`neurobrain-selector-v1`) on the same set, raw `adapter_v1_eval.json`,
511 s: exact 0.739, answerable exact 0.591 (107/181), abstain recall 0.982, abstain precision **0.671**, over-select
0.033, 0 errors; fixtures 9/9 and 6/6; no citation on 53 of 181 answerable rows (29%), 11 of 28 on LongMemEval. It
would fail this gate on abstain precision alone. These are the numbers v2 has to beat on over-abstention.

## Promotion gate v2 (fixed before any v2 adapter result exists)

Same rules as v1; only the answerable-exact bar moves with the new comparator. The adapter, served through
`scripts/deploy_selector.sh` and scored with `scripts/eval_selector.py` on `data/selector_v2/eval_sealed.jsonl`, is
promoted only if:

1. Abstain recall is at least **0.50**.
2. Abstain precision is at least **0.85**.
3. Answerable exact is at least **0.510** (comparator 0.530 minus 0.02), i.e. at least **93 of 181** rows.
4. All 9 answerable fixtures pass, and at least 5 of the 6 near-miss fixtures return no citation.
5. No parse or request errors.

If it misses any item, it stays an experiment and the app keeps the official model.

## Adapter v2 result: passes the gate

Kaggle T4 run (data commit `8496da4`, 2,808 rows, 351 optimizer steps, 7,944 s, peak 7.6 GiB); training loss fell
from 0.081 (first tenth) to 0.014 (last tenth). Dev: exact 0.759, abstain recall 0.886, abstain precision 0.836,
0 parse errors (v1 on its dev: 0.780 / 0.991 / 0.772). Deployed with `scripts/deploy_selector.sh` as
`neurobrain-selector-v2`. Sealed set, raw `adapter_eval.json`, 617 s:

| Model | Exact match | Answerable exact | Abstain recall | Abstain precision | Over-select | No citation on answerable | Errors |
|---|---|---|---|---|---|---|---|
| Converted base | 0.433 | 0.530 (96/181) | 0.273 | 1.000 | 0.050 | 0/181 | 0 |
| Adapter v1 (reference) | 0.739 | 0.591 (107/181) | 0.982 | 0.671 | 0.033 | 53/181 | 0 |
| Adapter v2 | **0.780** | **0.773 (140/181)** | **0.791** (87/110) | **0.870** (87/100) | 0.077 | 13/181 | 0 |

| Gate item | Needed | Adapter v2 | Result |
|---|---|---|---|
| 1. Abstain recall | ≥ 0.50 | 0.791 | pass |
| 2. Abstain precision | ≥ 0.85 | 0.870 (87/100) | pass (three more wrong refusals, 87/103, would fail it) |
| 3. Answerable exact | ≥ 93 of 181 | 140 of 181 | pass |
| 4. Fixtures | 9/9 answerable, ≥ 5/6 near-miss abstain | 9/9, 6/6 | pass |
| 5. Errors | 0 | 0 | pass |

Rebalancing the data fixed most of v1's over-abstention (no citation on 13 of 181 answerable rows, v1 53) while
keeping all six demo near misses abstaining. On LongMemEval, 4 of 28 answerable rows get no citation (v1: 11); that
slice is small (30 rows) and its abstain precision is 0.2 (1 of 5), so conversation-style refusals remain the
weakest area. HotpotQA abstain precision is 0.688. The precision margin is three rows, so treat v2 as a clear
improvement that passes the agreed bar, not as a large safety margin.

**Using it in the app (opt-in):** `answer()` reads `NEUROBRAIN_SELECTOR_MODEL` (default `qwen3.5:4b`), so on a Mac
with this model in Ollama run `export NEUROBRAIN_SELECTOR_MODEL=neurobrain-selector-v2` before starting the app.
Note extraction (`generate()`) still uses `qwen3.5:4b`; the adapter was trained only for citation selection.

## Live app check (25 Nov 2026, evening)

Screenshots of the chat app showed wrong answers. Replaying them on a copy of the app's database:

1. **Wrong citations** ("When is the violet demonstration" → the Saffron Bridge beta-release line; same for
   "launch party"): the running app was the main checkout on `demo-week-2026-11`, so it used `qwen3.5:4b`, not v2.
   With `NEUROBRAIN_SELECTOR_MODEL=neurobrain-selector-v2` every replayed question gave the right citation or none.
2. **Book club page never stored**: the edited Notion page (the same page as the Saffron Bridge notes) was rejected
   whole because 2 of 8 model quotes were not exact (a capital letter, a dropped word). Fixed: `extract_notes`
   keeps the source's own span for a case-only difference and drops quotes it cannot find; it still fails if none
   verify, and `import_observation` still rejects any altered note.
3. **Later sentences skipped**: one extraction call on the 1,300-character paragraph stopped after the first half,
   missing every update (Daniel picks the books, Aisha, $8 dues, *Salt and Signal*). Fixed: extraction runs per
   ~600-character window (`windows()`); on the retyped page 13 notes are stored instead of 7.

Still wrong after the fixes, on the retyped page with v2 (not on the real Notion text, which needs the user's token):

| Question | Answer | Why |
|---|---|---|
| Who picks the books? | none | Search is keyword-only; "picks the books" shares no word with "handed book selection to Daniel" |
| How much are the dues? / Who collects the dues? | the old $5 / Daniel line | All three lines reach the selector; it cites the outdated one. v2 never trained on updated facts (knowledge-update questions were excluded) |
| What is the current book? | none | "switched to Salt and Signal" was not in the top five search results |

Meeting time and place, parking, and the near misses (violet demonstration, holiday party) were right.
