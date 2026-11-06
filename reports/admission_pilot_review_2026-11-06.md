# Admission pilot: one human review — 6 November 2026

**Input:** `admission_pilot_v0_blind_review (1).xlsx`, SHA-256 `649f580cd2d0ec6a2f27c470d8f1e67d1ff75ef8efc7951243d939f2e69e8396`. The workbook has one sheet, 80 unique expected IDs, unchanged context/candidate text, and no formulas. Every row has a valid `action`, `type`, `scope`, `sensitivity`, `source`, and nonempty rationale. Nineteen rows include review notes. The workbook was read without modifying it.

| Field | Match with assistant draft | Human review distribution |
|---|---:|---|
| Action | 80/80 | 48 keep, 32 skip; no uncertain rows |
| Type | 74/80 | 9 types used |
| Scope | 73/80 | 42 project, 32 session, 6 person |
| Sensitivity | 72/80 | 73 ordinary, 5 personal, 2 restricted |
| Source | 80/80 | All fictional assistant authored |

Fourteen rows differ on at least one field. These are descriptive comparisons with the original assistant drafts. The assistant had already shown draft labels and explanations in chat before this review arrived, so the action match is **not** an independent reliability or accuracy estimate. No inter-human Cohen's kappa is available.

## Accepted resolutions

| ID | Draft → human review | Proposed resolution and reason |
|---|---|---|
| 03-02 | scope person → project | `person`: household size can inform planning beyond one meal project. |
| 03-03 | type fact → milestone; scope person → project; sensitivity personal → ordinary | `fact / person / personal`: a recurring household schedule is not a one-time milestone. |
| 04-02 | scope person → project | `project`: the gap is specific to this course of study. |
| 04-03 | type decision → milestone; scope person → project; sensitivity personal → ordinary | `decision / project / personal`: a newly reserved weekly slot is a plan, and precise recurring availability is personal. |
| 04-04 | sensitivity personal → ordinary | `ordinary`: a general teaching preference is low sensitivity. |
| 05-00 | type preference → requirement | `requirement`: step-free access is stated as a need; do not infer its cause. |
| 08-03 | scope person → project; sensitivity personal → ordinary | `project / ordinary`: the setup belongs to this guitar. |
| 09-03 | type decision → requirement | `requirement`: “Use” is an instruction; a choice among options is unstated. |
| 10-00 | type fact → decision; sensitivity ordinary → personal | `fact / personal`: the named responsibility is stated, but the decision to assign it is not. |
| 12-00 | sensitivity personal → ordinary | `ordinary`: a general tutoring feedback preference is low sensitivity. |
| 12-01 | scope person → project; sensitivity personal → ordinary | `project / ordinary`: the assessment belongs to this learning activity. |
| 12-02 | scope person → project | `project`: the weakness concerns this language subject. |
| 13-04 | sensitivity personal → ordinary | `ordinary`: a broad running preference is low sensitivity. |
| 15-03 | type decision → correction | `correction`: the sentence explicitly replaces Bluetooth with a wired link. |

The user accepted all 14 proposed resolutions. They are recorded in `data/admission_pilot_v1_labels.csv` with individual reasons; every row still has `status=draft`. Seven field values across four rows changed from the human workbook; the other proposed resolutions confirmed the human choices. The v1 label file has SHA-256 `5c9a04207e556761d6e04a89c9514c2a1a3ba7e9982e285c31beee554981f652`.

The review notes also flagged useful cases where the fields matched: keyboard use and peanut exclusion do not reveal their underlying cause; a one-time wheelbarrow noise is weaker than a recurring fault; and changed dates can be both corrections and milestones. The frozen v1 guide now states tie-break rules for these patterns. A delayed 20-row masked-label repeat check remains before expansion or further training.
