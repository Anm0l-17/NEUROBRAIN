# Citation selector v3: data and gate before training (26 Nov 2026)

Adapter v2 passed its gate (`reports/selector_v2/README.md`), but the live app check showed it citing outdated
lines when a page records a change. Asked "How much are the dues?", it cites "Dues are $5 a month, collected by
Daniel" and ignores "dues went up to $8 a month". v2's data excluded LongMemEval knowledge-update questions, so it
never trained on an old value and a new value side by side.

`data/selector_v3` is built by `scripts/build_selector_data.py`; data commit `22c5f7f`, pinned in `kaggle/selector_train.py`.
v3 changes only the data. The request format (`extract.selection_payload` / `SELECT_SYSTEM`) and the notebook
settings are the same as v2's: seed 17, lr 2e-4, rank 16, accumulation 8, one epoch.

## Update policy

**The gold citation is the line holding the current value, and only that line.** The app shows cited lines
word for word, so citing the old line as well would still put "$5" on screen. Outdated lines stay in the evidence
and are listed in each row's `stale` field. The selector sees no dates, and lines arrive in random order, so
"current" must be readable from the line's own wording ("went up to", "now", "took over", "moved to").

Rows built from the templates come in six kinds. The other five stop the model from simply picking whichever line
has a change word:

| Kind | Evidence | Gold |
|---|---|---|
| current | old line (sometimes one line holding two attributes, like the dues line) + update line | update line |
| sibling | only another attribute changed (e.g. asking the fee when only the organiser changed) | the old line, which is still true |
| original | old + update, question says "at first" / "before" | old line (its update line never repeats the old value) |
| lone_old / lone_update | just one of the two | that line |
| absent | the asked attribute is not in the evidence at all | nothing |

## Data

| Split | Rows | Empty | Base mix (as v2) | LongMemEval update | Update templates | Fixtures |
|---|---|---|---|---|---|---|
| Train | 3,676 | 19.9% | 2,901 (SQuAD 1,150, HotpotQA 1,400, LongMemEval 351) | 75 (25 questions × 3 renders) | 700 | — |
| Dev | 386 | 38.6% | 323 | 3 | 60 | — |
| `eval_sealed.jsonl` | 261 | 45.6% | 246 (SQuAD 150 with 60 answerable, HotpotQA 96) | — | — | 15 (same rows as v1/v2) |
| `eval_update_sealed.jsonl` | 267 | 19.1% | — | 19 | 240 | 8 (book club) |

- **Two sealed files.** `eval_sealed.jsonl` is scored exactly as v2's sealed set was, for gate items 1 to 5.
  `eval_update_sealed.jsonl` holds every update row, for items 6 to 9. `scripts/eval_selector.py` is unchanged.
- **Fresh sealed sets.** No sealed row shares a question or an evidence line with the v1 or v2 sealed sets (both
  were used for a decision), or with any train/dev row. Fixtures are the exception, and the builder asserts this.
  Every single-session/multi-session LongMemEval question has now been shown by an earlier sealed set or trained
  on, so `eval_sealed.jsonl` has **no LongMemEval slice** (v2 had 30 rows). v2's sealed LongMemEval questions now sit in
  train and dev.
- **Held-out templates.** The sealed update rows use attribute families (meeting frequency, phone extension,
  equipment storage, car, morning drink), entity kinds and names that never appear in train or dev. Train/dev use
  weekday, venue, start time, fee, organiser, deadline, member count, chat app, city and job. The words "dues",
  "Daniel", "Aisha" and "Harbor Lights" never appear in a training template row; the builder asserts it.
- **LongMemEval knowledge-update** (MIT): kept only where the newest answering turn contains the answer and the
  older turns do not (42 of 72 questions, plus 6 abstention questions). Split by question: 40% sealed, 10% dev,
  50% train. The text cue is often weak ("I've tried four so far"), so this slice is small and noisy, and it is
  reported but not gated. `stale` lists only the older answering turns; a distractor can hold another
  outdated value (e.g. the Crash Course row's "my 12th video").
- **Book-club fixtures** (sealed only): the notes stored from the user's page in the 25 Nov live check, with all five lines
  shown. They cover dues amount, dues collector, venue, start time, which Thursday, who picks the books, the current book (gold:
  "no longer The Glass Orchard" plus "switched to Salt and Signal", since the second only says "it"), and one near miss ("How much is the library room fee?", where no line states it).
- LoCoMo is not used. Licences are in `data/selector_v3/NOTICE.md`.
- Deterministic: two builds under different `PYTHONHASHSEED` values give identical files (hashes in `manifest.json`).

## Comparators on the v3 sealed files (scored before any v3 training)

Raw outputs are in this folder: `converted_base_eval.json`, `converted_base_update_eval.json`, `adapter_v2_eval.json`,
`adapter_v2_update_eval.json`.

`eval_sealed.jsonl`:

| Model | Exact | Answerable exact | Abstain recall | Abstain precision | Over-select | No citation on answerable | Errors |
|---|---|---|---|---|---|---|---|
| Converted base | 0.510 | 0.599 (85/142) | 0.403 | 1.000 | 0.063 | 0/142 | 0 |
| Adapter v2 | 0.816 | 0.789 (112/142) | 0.849 | 0.927 | 0.092 | 8/142 | 0 |

Fixtures: base 9/9 answerable, 4/6 near miss; v2 9/9, 6/6.

`eval_update_sealed.jsonl`:

| Model | Current-value exact | Stale line cited | Sibling + lone exact | Original exact | Absent exact | LongMemEval update exact | Book club | Abstain precision (file) |
|---|---|---|---|---|---|---|---|---|
| Converted base | 0.283 (26/92) | 82/115 | 83/83 | 9/16 | 35/49 | 8/19 | 1/8 (dues 0/2) | 1.000 |
| Adapter v2 | 0.500 (46/92) | 61/115 | 83/83 | 6/16 | 49/49 | 8/19 | 2/8 (dues 0/2) | 0.926 |

v2 reproduces the live failure. It fails both dues questions and cites a stale line on more than half the rows that
have one. In 55 of those 61 it cites only the old line, picking the outdated value over the new one
(the converted base mostly cites both: 54 of 82).

## Promotion gate v3 (fixed before any v3 adapter result exists)

The adapter is served through `scripts/deploy_selector.sh` and scored with `scripts/eval_selector.py` on both
sealed files. It is promoted only if it passes every item below.

On `eval_sealed.jsonl`, with the v2 rules unchanged:

1. Abstain recall is at least **0.50**.
2. Abstain precision is at least **0.85**.
3. Answerable exact is at least **0.579** (comparator 0.599 minus 0.02, the v2 rule), i.e. at least **83 of 142**.
   Also, so v3 does not regress from the model it replaces: at least **107 of 142** (adapter v2's 112 minus 5).
4. All 9 answerable fixtures pass, and at least 5 of the 6 near-miss fixtures return no citation.
5. No parse or request errors on either file.

On `eval_update_sealed.jsonl` (new):

6. **Update accuracy.** Current-value exact (`update_current`) is at least **0.75**, i.e. at least **69 of 92**
   (v2: 46).
7. A stale line is cited on at most **28 of 115** rows that have one, i.e. at most 25% (v2: 61).
8. **Book club.** Both dues fixtures pass, and at least **6 of 8** book-club fixtures pass (v2: 2/8).
9. **No shortcut.** Sibling, lone_old and lone_update exact together are at least **79 of 83** (v2: 83). File-wide
   abstain precision is at least **0.85** (v2: 0.926).

Reported, not gated: `update_original` (16 rows), `update_absent`, and `longmemeval_update` (19 rows, weak text
cues). If the adapter misses any item, it stays an experiment and the app keeps v2 as the opt-in model.

How to count items 7 and 8 from the raw output: a row "cites a stale line" when its prediction shares any ID with the
row's `stale` list. Book-club rows have source `fixture_update`. A fixture passes on an exact match.

## Adapter v3 result: fails the gate by one item (27 Nov 2026)

**Not promoted. The app keeps `neurobrain-selector-v2`.** v3 passes eight of the nine items and misses item 8, the
book club fixtures. The rule above was written before training, so it stays an experiment.

Kaggle T4 run (data commit `22c5f7f`, 3,676 rows, **459** optimizer steps, not the 460 estimated below: the last 4
rows never completed a step; 13,445 s; peak 7.47 GiB). Training loss fell from 0.083 (first tenth) to 0.012 (last
tenth). Deployed with `scripts/deploy_selector.sh` as `neurobrain-selector-v3` (adapter keys matched before merge).

| Gate item | Needed | Adapter v3 | Adapter v2 | v3 result |
|---|---|---|---|---|
| 1. Abstain recall | ≥ 0.50 | 0.908 | 0.849 | pass |
| 2. Abstain precision | ≥ 0.85 | 0.923 | 0.927 | pass |
| 3. Answerable exact | ≥ 83 and ≥ 107 of 142 | 114 | 112 | pass |
| 4. Fixtures | 9/9, ≥ 5/6 near-miss abstain | 9/9, 6/6 | 9/9, 6/6 | pass |
| 5. Errors, both files | 0 | 0 | 0 | pass |
| 6. Current value exact | ≥ 69 of 92 | 92 | 46 | pass |
| 7. Stale line cited | ≤ 28 of 115 | 6 | 61 | pass |
| 8. Book club | ≥ 6 of 8, both dues | **5 of 8, 1 of 2 dues** | 2 of 8, 0 of 2 | **fail** |
| 9. Sibling + lone, precision | ≥ 79 of 83, ≥ 0.85 | 83, 1.000 | 83, 0.926 | pass |

Reported, not gated: `update_original` 15/16 (v2 6/16), `update_absent` 49/49 (49/49), `longmemeval_update` 14/19
(8/19). Sealed file: exact 0.851 (v2 0.816), over-select 0.056 (0.092), no citation on 9 of 142 answerable rows
(8). Raw: `adapter_eval.json` (440 s), `adapter_update_eval.json` (406 s); items computed by [`gate.py`](gate.py),
which reproduces the v2 and base figures above.

The three book club misses:

| Question | v3 cited | Gold |
|---|---|---|
| Who collects the dues? | only the old "$5 … collected by Daniel" line | "Collecting dues then passed to a new member, Aisha" |
| What is the current book? | only "no longer The Glass Orchard" | that line **and** "switched to Salt and Signal" |
| How much is the library room fee? | the "$8 … library room fee" line | nothing (no line states the fee; v2 fails it too) |

How to read this:

- On the update rows built from templates v3 is far better than v2. On the older kind of sealed rows it stays about level: two more answerable rows exact, abstain precision 0.923 against 0.927, and one more answerable row with no citation. Of the 6
  rows where it still cites an outdated line, 5 cite only the old one.
- Template rows scoring 92/92 are probably easier than real notes. The attribute families and names were held
  out, but the sentence style was not. On the real page it passes 5 of 8.

**Kaggle dev numbers do not describe the served model.** On `dev.jsonl` the notebook reported exact 0.497, abstain
recall 0.725, abstain precision 0.857 and **141 parse errors of 386** (v2: 0.759, 0.886, 0.836, 0). Twenty of the
failed rows were replayed through the served model: all 20 replies were valid and 16 were exactly right, both with
the app's JSON schema and without it ([`kaggle_failed_rows.json`](kaggle_failed_rows.json)). The cause on Kaggle was
not established; the notebook saves no raw replies. The sealed gate above had 0 errors.

## Running it on Kaggle (you start this yourself)

Train has 3,676 rows, which is 460 optimizer steps. v2 took 7,944 s for 351 steps, so expect about **2 h 55 min** on
one T4.

1. Open the selector notebook on Kaggle and replace its code with `kaggle/selector_train.ipynb` from this branch
   (File → Import Notebook, or paste each cell).
2. Settings: Accelerator **GPU T4 x1**, Internet **On**.
3. Leave `SMOKE = True`. Click **Save Version → Save & Run All**. Wait for `SELECTOR_DONE` at the end of the log
   (a few minutes).
4. Set `SMOKE = False`. Click **Save Version → Save & Run All** again. Close the tab; it runs in the background
   for about 3 hours.
5. When it finishes, download `/kaggle/working/selector_v3/adapter.zip` from the version's Output tab.
6. Hand the zip back to Claude to deploy it as `neurobrain-selector-v3` and score it against this gate.
