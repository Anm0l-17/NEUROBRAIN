# Stage B Session 09 — Batch A authoring and review closure

Batch A's authoring and solo review milestone is complete: 500 fictional candidates across 25 scenarios, with all five 100-row review sheets submitted. All recorded label differences are resolved. Labels remain draft for the later full-corpus data gate; no split or training has been performed. This closes the Batch A milestone, not all of Stage B or the separate learner practice exercises.

## Canonical label sources

Original draft JSONL and submitted CSV files remain unchanged. Apply these reviewed label sources by `example_id`; do not treat the original assistant type fields as adjudicated labels.

| Set | Reviewed label source | Rows |
|---|---|---:|
| 01 | `data/admission_batch_a_adjudicated_01.csv` | 100 |
| 02 | `data/admission_batch_a_adjudicated_02.csv` | 100 |
| 03 | `data/admission_batch_a_review_03_completed.csv` | 100 |
| 04 | `data/admission_batch_a_adjudicated_04.csv` | 100 |
| 05 | `data/admission_batch_a_adjudicated_05.csv` | 100 |

Set 03 has no differences requiring a separate adjudicated file. The manifest records it as a single-human-reviewed draft. Sets 01, 02 and 04 resolve generic presentation-rule sensitivity using the user's approved `ordinary` precedent. Set 05 records the two explicitly accepted type changes.

## Verification

- **Passed:** 500 unique IDs; 25 groups of 20; both keep and skip in every group.
- **Passed:** every submitted ID, context and candidate matches its source draft; allowed labels and nonempty review rationales on all 500 rows.
- **Passed:** reviewed keep/skip agrees with binary draft labels; all 14 draft/review/adjudicated asset hashes and ID lists match the manifest.
- **Passed:** no normalized exact candidate duplicates within Batch A or against the 80-row pilot.
- **Passed:** all draft splits are unassigned and all 500 rows share `assistant-structured-scenarios-a1`; adjudicated rows retain draft status.
- **Recorded:** five normalized character-similarity pairs at threshold 0.78 within Batch A; none against the pilot. The pairs below have consistent keep/skip labels and remain unchanged. Character similarity cannot rule out semantic paraphrases.

| Candidate pair | Similarity |
|---|---:|
| batch-a-03-03 / batch-a-09-03 | 0.820 |
| batch-a-05-12 / batch-a-19-12 | 0.784 |
| batch-a-06-12 / batch-a-14-09 | 0.881 |
| batch-a-07-13 / batch-a-12-13 | 0.821 |
| batch-a-09-16 / batch-a-14-11 | 0.795 |

Resolved label counts: **299 keep / 201 skip**. Type counts: decision 21, preference 26, requirement 75, milestone 25, correction 50, unresolved_issue 50, fact 52, transient 126, acknowledgment 75. Sensitivity: **500 ordinary**.

## Limits and next step

This is one person's review compared with assistant drafts. No independent reliability estimate or model accuracy was measured. Nonempty rationales establish annotation coverage, not that every interpretation is objectively correct. Simple recurring structures, class/type cues and synthetic context limit representativeness. All-ordinary sensitivity provides no coverage of personal, restricted or ambiguous privacy cases. Usefulness remains separate from storage permission.

Keep all connected Batch A examples in one partition during Session 13's grouping audit. Twenty-five scenario names do not create 25 independent template families; this batch alone cannot support a credible three-way evaluation split.

Session 10 next authors Batch B: 500 additional candidates across 25 new scenarios, varying domain, vocabulary and actual sentence/context structure. Include fictional personal/restricted and uncertain cases and useful/irrelevant near matches under the annotation guide, with human review. Merely assigning new template identifiers does not establish independence. Sessions 11–12 then target 2,000 total examples, followed by the grouped split audit and remaining Stage B data gates before training.
