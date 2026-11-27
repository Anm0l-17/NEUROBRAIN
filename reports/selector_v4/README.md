# Citation selector v4: distillation data (28 Nov 2026)

**Status: data built, not trained yet. The app keeps `neurobrain-selector-v2`.**

v3 passed 8 of the 9 gate items and failed item 8, the book club fixtures (`reports/selector_v3/README.md`).
It cited the old "$5 … collected by Daniel" line for "Who collects the dues?". It cited only one of the two lines
needed for "What is the current book?". And for "How much is the library room fee?" it cited a line that only
mentions the fee.

v4 is **knowledge distillation**, "the father teaches the son". Claude Sonnet 5.5 (the teacher) wrote and labelled
new training rows, and our small Qwen LoRA (the student) is fine-tuned on them. No weights are edited directly. Training
settings are unchanged from v2/v3: seed 17, lr 2e-4, rank 16, accumulation 8, one epoch.

## How the rows were made

1. **Teacher.** Eight Sonnet runs, each in its own domain (work, household, school, sport, housing, software,
   community, personal admin), wrote 110 scenarios each, 880 in all. A scenario is a question plus five
   conversation-style note lines, with the lines to cite. Styles are mixed on purpose: full sentences, lowercase
   fragments, pronouns ("it", "she") and updates with no cue word. That way the student cannot learn "pick the fragment".
   The policy is v3's: cite only the current-value line; cite both lines when the question asks about the change or the
   current value needs two lines; cite only the old line for "at first"; cite nothing when no line states the value.
2. **Kinds**:
   - `current`: old and new value
   - `two_attr`: one old line holds two facts and each fact is updated separately. This is the "who collects" shape.
   - `split`: the current value needs two lines
   - `change`: the question asks about the change itself
   - `sibling`
   - `original`
   - `lone`
   - `near_miss`: the topic word or a number appears, but the value does not
3. **Second pass.** Eight new Sonnet runs labelled every scenario **blind**: lines shuffled and lettered A to E,
   no teacher labels shown. A scenario is kept only when both passes cite exactly the same lines.
4. `scripts/build_selector_v4.py` turns the kept scenarios into rows. It uses v3's own `row()` function, so the
   format and citation IDs are the same. It merges them with v3's train/dev lines (kept byte for byte) and shuffles.
   Two runs give identical files.

| Kind | Teacher wrote | Both passes agreed (kept) |
|---|---|---|
| current | 200 | 198 |
| two_attr | 120 | 118 |
| split | 80 | **45** |
| change | 80 | 79 |
| sibling | 96 | 96 |
| original | 64 | 64 |
| lone | 64 | 64 |
| near_miss | 176 | 176 |
| **Total** | **880** | **840** |

Most dropped `split` rows had a "no longer X" line next to a line that states the new value fully on its own. There
the second pass cited only the new line, which is defensible. The kept `split` rows are mostly the ones where the
second line really needs the first (as with "switched to it").

**Third review.** An independent checker then read the kept rows. It flagged 9 `split` rows where one gold line
already states the value alone (the other is only a reason or the old holder), plus 1 row (`g5-003`) that answers a
wifi-password question with a router-password line. All 10 were dropped as well, leaving 840 (850 agreed − 10). IDs
of every dropped row are in [`dropped_rows.json`](dropped_rows.json).

## Data

| Split | Rows | Teacher rows | Empty targets |
|---|---|---|---|
| Train | 4,449 (v3 3,676 + 773) | 773 | 895 (20.1%; v3 19.9%) |
| Dev | 453 (v3 386 + 67) | 67 | 160 |

Hashes are in `data/selector_v4/manifest.json`. v4 has **no sealed file of its own**. It is scored on v3's
`eval_sealed.jsonl` and `eval_update_sealed.jsonl`, both unchanged.

## Checks

- Sealed files unchanged: the sha256 of `data/selector_v{1,2,3}/eval*sealed.jsonl` and `reports/selector_v3/gate.py`
  were recorded before any work and are identical after it. They are also listed in the manifest.
- **No teacher row names any fixture fact.** The builder refuses any row whose question or evidence contains, in any
  case, any of the following:
  - book, dues, Daniel, Aisha, Priya, Mira, Rohan
  - Harbor Lights, Saffron Bridge, amber lighthouse, violet demonstration, pink submarine, teal harbour
  - Glass Orchard, Salt and Signal, Corner Grind, Wharf Road, library room fee
  - the sealed update file's held-out names and families (phone extensions and the others)

  `grep -ic` for the five named phrases plus dues, Daniel, Aisha, Glass Orchard, Salt and Signal and Harbor Lights
  on `teacher_rows.jsonl` gives **0**.
- No teacher question or line equals any question or line in the v1, v2 or v3 sealed files; the builder checks this,
  and none had to be dropped.
- **Merged train, honest note.** 5 rows already in v3's train contain the phrase "book club". They are LongMemEval
  chats where a person mentions their own book club, and they were in v3's training too. None is the fixture page.

## Caveat for reading the result

The teacher rows were shaped after seeing v3's three book-club misses. Gate item 8 still uses the unchanged fixtures,
but passing it is now weaker evidence that the model generalises than it was for v3. Items 6, 7 and 9 (held-out
names and families) remain the cleaner test.

## Promotion rule

The same 9-item gate as v3 (`reports/selector_v3/README.md`), on the same two sealed files, computed by
`reports/selector_v3/gate.py`. v4 becomes the default only if **all 9** pass; otherwise v2 stays.

## Your Kaggle steps (you run these)

Train has 4,449 rows, about **556 optimizer steps**. v3 took about 29 s per step, so expect **about 4.5 hours** on
one T4. First check that your weekly Kaggle GPU quota has at least 5 hours left (Kaggle → your profile → Settings or the
quota bar in the notebook editor).

1. Open Kaggle and create a new notebook (or open the old selector notebook).
2. **File → Import Notebook**, and choose `kaggle/selector_train_v4.ipynb` from this branch
   (download it from GitHub: branch `claude/blissful-boyd-f91497`, folder `kaggle`).
3. In the right-hand panel set **Accelerator: GPU T4 x1** and **Internet: On**.
4. In the second code cell, check that `COMMIT = "..."` holds a long 40-letter code (it is already filled in), not
   `SET_ME`.
5. Leave `SMOKE = True`. Click **Save Version → Save & Run All**. Wait a few minutes until the log ends with
   `SELECTOR_DONE`. This is a short test run.
6. Change `SMOKE = True` to `SMOKE = False`. Click **Save Version → Save & Run All** again. You can close the tab;
   it runs in the background for about 4.5 hours.
7. When it finishes, open that version's **Output** tab and download `selector_v4/adapter.zip`.
8. Give `adapter-v4.zip` (the downloaded zip) back to Claude. Claude deploys it as `neurobrain-selector-v4`,
   scores the 9 gate items, and runs the live check on a read-only copy of the database.

## Result

Not trained yet.
