# Stage B Session 09 — first 100-row human review

**Input:** `data/admission_batch_a_review_01_completed.csv`, supplied by the user as pasted text; SHA-256 `b5eee46138f553489b75893327fe7ecd3ff829750b321d83d73140b622f63aee`. All 100 expected IDs are unique and present. Context and candidate text match the draft exactly. Every row has allowed values in all five label fields and a nonempty rationale; eight rows have review notes. The original draft and submission are preserved.

| Field | Match with assistant draft |
|---|---:|
| Action | 100/100 (59 keep, 41 skip) |
| Type | 100/100 |
| Scope | 100/100 |
| Sensitivity | 99/100 |
| Source | 100/100 |

**Adjudicated sensitivity:** `batch-a-04-10`, “Practice prompts must be available in large print.” The draft marked sensitivity `ordinary`; the user's submitted review marked `personal` and notes that a member access need is possible but no person or reason is named. The user then explicitly selected `ordinary` for this general rule, while retaining `keep / requirement / project`. The original review remains unchanged. `data/admission_batch_a_adjudicated_01.csv` records the accepted result and reason; all 100 rows remain `draft` for the larger data gate.

These are descriptive draft-versus-human matches. They do not measure independent human agreement or model accuracy. The first tranche is reviewed and its only difference resolved. Session 09 still needs 300 more draft candidates and human review of all remaining tranches before its 500-row target is complete.
