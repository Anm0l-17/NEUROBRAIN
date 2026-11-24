# Batch B individual clarification log

Responses are annotation discussions about fictional examples. Preserve the original submissions and canonical labels. Resolutions below apply to the original context plus the recorded clarification; they are not applied training labels for the original, unaugmented rows.

## Current decision — 8 November 2026 — all 28 remain unresolved

The user's latest correction supersedes every individual interpretation below. The Spanish-session keep and easier-version skip are withdrawn; the crossing proposal is withdrawn. Earlier statements and counts below are historical only and must not be applied as active labels or added factual context.

All 28 original rows retain `action=uncertain`, `type=uncertain`, `scope=uncertain`. Each is judged independently using only its supplied `prior_context` and `candidate_text`. No other candidate supplies missing history. The workbook does not contain the missing referents; no fictional answers should be invented to complete these existing examples. An unanswered clarification stays unresolved and is not converted to keep or skip. Clarification collection for this list is closed without answers; uncertainty itself is the recorded outcome.

The latest user instruction restores `sensitivity=uncertain` for these eight IDs: `batch-b-01-00`, `batch-b-07-01`, `batch-b-08-03`, `batch-b-09-09`, `batch-b-10-06`, `batch-b-14-13`, `batch-b-18-08`, `batch-b-23-07`. The other 20 retain ordinary sensitivity. Do not infer a medical, accessibility, dietary or other private reason.

**Versioned labels:** `data/admission_batch_b_adjudicated_v1_1.csv` is the current 500-row label snapshot. The only label difference from the previous accepted snapshot is `batch-b-07-01` sensitivity, restricted to uncertain, explicitly superseding the earlier acceptance. This is a user override of guide v1.2's explicit-privacy sensitivity rule, not a general guide revision. The sentence's explicit privacy warning remains in the candidate and adjudication note; uncertainty does not grant storage/sharing permission or revoke the privacy request. No private reason is needed to honor that request.

Counts remain **319 keep, 153 skip, 28 uncertain**. Sensitivity counts are **412 ordinary, 38 personal, 42 restricted, 8 uncertain**. All rows remain draft. The original CSV, original workbooks and their blank clarification responses are preserved; the workbook remains an earlier snapshot. These 28 must be excluded explicitly from any later binary usefulness training input while they remain uncertain; exclusion is not a skip label. No binary input or training run is created here.

## Historical individual discussion — superseded in full

## batch-b-00-02 — 8 November 2026 — further clarification needed

**Candidate:** That crossing is still awkward.

**Supplied prior context:** A fictional commuter plans a bicycle route for the next six months. The stored route already avoids Quarry Road.

**User response, verbatim:**

> So for the batch B zero zero two, the crossing in this means that for the context, if you are looking for the context is that we're making a plan, and the plan says about bicycle route. So while taking the note of the crossing, we should take note of the crossing and perhaps the exact number. If there is uncertainty in that, we should try to check for the previous record, the record which the user used previously, or any clue which the user has given, or any observation which you observed during the planning stage, which makes sure that, okay, user is speaking about this specific crossing. So we're gonna take that crossing as a keep, and the type should be project-based, scope should be ordinary, and sensitive should be ordinary, scope should be implemented.

**Interpretation:** The reviewer wants to retain a useful bicycle-route issue and resolve its referent from available prior evidence before asking again. This is a proposed retrieval rule, not evidence that a particular crossing has been identified or that retrieval is implemented. Only authorized available records may supply that evidence; do not invent observations.

**Evidence checked:** The row's supplied context identifies a route plan and an existing Quarry Road avoidance constraint, but no crossing name/number or specific difficulty. Other candidate rows in this scenario are separate annotation examples, not automatically prior conversation history; in particular, the later bridge-replacement candidate cannot establish this row's referent.

**Field mapping if the missing referent and difficulty are supplied:**

| Field | Proposed value | Reason |
|---|---|---|
| action | keep | Reviewer's requested judgment, conditional on enough context to identify the issue. |
| type | unresolved_issue | An ongoing difficulty relevant to the route plan. |
| scope | project | Applies to the bicycle-route plan. |
| sensitivity | ordinary | No personal or restricted detail supplied. |
| source | fictional_assistant_authored | Original candidate provenance is unchanged; the follow-up is user-authored and recorded above. |
| status | draft | No full-corpus gate has passed. |

`project-based` maps to scope `project`; `ordinary` belongs to sensitivity; `implemented` is not an allowed scope or annotation status. Do not silently map it to a valid value.

**Pending question:** In this fictional example, which crossing (name, number, or unambiguous description) does the commuter mean, and what makes it awkward? Alternatively, provide the specific prior record that establishes those details.

**Saved outcome:** Response recorded; no canonical label or source-text changes. Current labels remain `uncertain / uncertain / uncertain / ordinary / fictional_assistant_authored`, with status `draft`. All 28 Batch B actions still require resolution.

## batch-b-01-00 — 8 November 2026 — clarified usefulness

**Candidate:** I cannot manage those sessions anymore.

**Supplied prior context:** A fictional language-exchange member prepares for weekly Spanish conversations. A stored note already says meetings last forty minutes. The work is educational, with no diagnosis or medical assessment.

**User clarification, verbatim:**

> session refers to the spanish session

**Resolved interpretation:** The speaker reports that the current Spanish conversation sessions are no longer manageable. This is a useful open issue for the language-exchange project. The referent is now identified, so an exact replacement schedule or format is not required to retain the issue as unresolved. No reason, diagnosis, cancellation, or replacement arrangement has been supplied; do not infer any of them.

| Field | Resolved value for clarified example | Reason |
|---|---|---|
| action | keep | The ongoing difficulty matters to future Spanish-session planning. |
| type | unresolved_issue | The current arrangement is a problem; a solution remains unspecified. |
| scope | project | Applies to this Spanish language-exchange activity. |
| sensitivity | ordinary | A generic task-specific difficulty reveals no precise availability or sensitive reason. |
| source | fictional_assistant_authored | Original candidate origin; user-authored clarification is attributed separately above. |
| status | draft | Full-corpus gates remain pending. |

**Retainable wording:** The speaker reports that the current Spanish conversation sessions are no longer manageable; the required adjustment remains unspecified.

**Saved outcome:** Clarified interpretation recorded; one of the 28 has enough context for a usefulness resolution, with 27 remaining. Original canonical CSV and workbook remain unchanged historical snapshots (28 uncertain actions); any consolidated revised dataset must include this clarification alongside the new labels to avoid labeling unseen context.

## batch-b-01-03 — 8 November 2026 — explicit reviewer skip

**Candidate:** Use the easier version next time.

**User decision, verbatim:**

> skip it

**Recorded decision:** `action=skip`, explicitly selected by the reviewer. The version and meaning of easier remain unspecified. This decision does not establish that the candidate is transient or has session scope, and does not create a general rule to convert unanswered clarifications into skip.

**Other fields:** Retain `type=uncertain`, `scope=uncertain`, `sensitivity=ordinary`, `source=fictional_assistant_authored`, `status=draft`. No additional rationale was supplied by the reviewer; do not invent one.

**Saved outcome:** Two action decisions recorded out of the original 28 (one clarified keep, one explicit skip); 26 remain pending. Original CSV and workbook remain unchanged historical snapshots. This is a reviewer adjudication, not new factual context.
