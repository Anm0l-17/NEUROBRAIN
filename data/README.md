# Admission pilot v0 — fictional fixtures

80 assistant-authored English examples in 16 independently authored scenario families.
Every example is fictional, and every label is a **draft pending human review**.
No personal notes, application memory, Kaggle data, or benchmark gold answers were used.

Each family has five chronologically ordered candidates (three positive, two negative).
Row order within each family was deterministically shuffled before assigning timestamps;
label order is not a feature. Context is a short fictional scenario description, not a
full evolving conversation. This is a convenience fixture, not a representative sample.

Split: first ten families train (50 records), next three validation (15), last three
test (15). Families and exact normalized candidate text are disjoint. Context repeats
within its family. Cross-family paraphrase similarity still needs human auditing.
The split differs from the full plan's 70/15/15 group target because this is a small
pipeline trial. All drafting happened together; these are not independently collected
or human-annotated evaluation records.

Positive: a reusable preference, decision, correction, specification, milestone or
specific unresolved problem. Negative: incidental session state, irrelevant observation
or acknowledgment. This initial set is deliberately easy and lacks challenging
ambiguity, realistic redundancy, evolving long histories, privacy-policy cases,
multilingual text and a realistic class distribution. It cannot validate deployment.

Fields follow docs/NeuroBrain_Session_Plan.md section 4. A rationale documents the intended
label but never enters model features. `provenance.kind` is fictional_assistant_authored;
`annotation_status` is assistant_draft_pending_human_review. Training refuses drafts
unless --allow-draft is explicitly supplied. That switch authorizes a pipeline trial,
not a declaration that labels are correct or that automatic exclusion is safe.

Test records have now been inspected for this report. Any tuning based on these
findings requires a new independently reviewed held-out set. Preserve v0 unchanged.
