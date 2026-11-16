# Prototype readiness, 16 November 2026 (update of the 13 November assessment)

**Approximately 65% (60-70%) engineering estimate** for the 23 November mentor prototype, up from about 60%. This is delivery readiness, not model accuracy, and live gates remain open whatever the average. The 13 November report is kept unchanged; the weights are the same.

| Component | Weight | 13 Nov | 16 Nov | What changed / what is still open |
|---|---:|---:|---:|---|
| Design, explanation, presentation materials | 10% | 60% | 60% | README and plan docs corrected (Day 5). No deck yet. |
| Selected inputs and observation controls | 15% | 65% | 70% | Each screen capture is its own source; a single-sentence fact links across screen and file routes (multi-line files do not). Live Notion and unsaved-window acceptance still unverified. |
| Structured extraction and evidence validation | 15% | 60% | 70% | Real local Qwen, F01-F11 about 1 s each, but Notion and OCR were simulated, pause/stop were not run, F09 was flaky once, and F07 passes only since the new filter. Model can still keep other vague text. |
| Local persistence, retrieval, versions, forgetting | 15% | 90% | 93% | Exact-content copies, sibling captures and raw-file residue are now forgotten. |
| Hosted persistence and provenance | 15% | 30% | 50% | Observation SQL, search and forget parity tested on local PostgreSQL 18; bridge `--hosted` exists. Never run on Supabase: no signed-in write, F12 or F13 evidence. |
| Chat and presentation interface | 10% | 65% | 70% | Reference guard narrowed (still refuses some ordinary questions, e.g. about the IT team); local bridge HTTP verified; `--hosted` bridge tested with mocks only. Real Open WebUI untested. |
| Privacy, admission and failure behaviour | 10% | 60% | 68% | Reviewer rounds closed over-forgetting bugs and a stale-version bug (forgetting a current text used to reactivate an outdated version; older versions now stay history only). Related gaps remain: whitespace-variant re-import is not blocked. Live denied-window and revoked-permission checks still open. |
| Integrated acceptance, timing, rehearsal | 10% | 20% | 20% | No live two-app walkthrough or route timing yet (Day 2). |
| **Total (weighted)** | **100%** | 57% | **64%** | Report as about 65%. |

Mandatory open gates: live Notion route, approved-window OCR on the presentation Mac, hosted write/retry/second-user evidence, Open WebUI connection, full rehearsal.
