# NeuroBrain mentor prototype · 23 November 2026

## Priority update · 11 November

The immediate delivery order is data extraction, structured notes, then questions answered from stored evidence. Qwen fine-tuning is deferred; use the existing pretrained local Qwen3.5 for extraction and evidence selection. Open WebUI is the existing chat interface, with the CLI retained for observation controls and inspection.

1. Verify a selected Notion page, selected saved file and explicitly approved VS Code window as separate input routes. Screen input uses local window capture followed by OCR; it does not give Qwen unrestricted desktop access.
2. Extract typed notes with exact supporting text, source, capture route, observation time and evidence spans. Apply privacy checks before model inference and validate extracted quotes before persistence.
3. Demonstrate local persistence and cited answers through the same database, including a clear no-evidence result. Connect this path to Open WebUI, then complete hosted persistence for the mentor demo.
4. Verify the whole path with a fresh unsaved screen fact, source updates and deletion. Model training is not a prerequisite for this milestone. Live capture, hosted writes and interface integration remain separate checks until demonstrated.

This priority order supersedes the scheduling emphasis below; the existing privacy and release checks still apply.

Revised 10 November. Acceptance is a live, supervised macOS session. The supervisor uses at least two approved applications, changes something on screen, and shows the teacher which observations NeuroBrain kept in the hosted database. The terminal is the operator interface. A third app is the target once two pass the whole workflow.

## What the teacher sees

1. Start an interactive CLI. Show the capture state, approved apps and windows, allowed documents, storage destination, and active admission model. The supervisor starts a time-limited demo session and explicitly enables automatic saving of permitted keeps to the demo Supabase project.
2. Add a fictional decision to the selected Notion demo page. For the page-data route, read changes through a read-only Notion connection granted access only to the dedicated demo page, with no child pages. Read saved changes to a selected Markdown file in VS Code. Attribute each retained note to its app and page or file. A selected Drive TXT/MD file remains the optional third source through C2.
3. With Auto Save off in VS Code, type a new fictional fact in an approved editor window and leave it unsaved. Read its visible pixels with local OCR. Query the database for the fact before saving, verify its screen provenance, then save the file and verify that the saved-file route does not create a duplicate. Page access in Notion and screen-capture permission are granted independently.
4. In a second terminal, watch a read-only query against the signed-in user's hosted rows. Each accepted note shows its text, source app, input route, observation time, revision or window-session reference, model/policy version, decision and evidence ID. Print “saved” only after the database acknowledges the transaction. Requery in a fresh process.
5. Show a transient remark, an ambiguous reference and an explicit do-not-store fixture. The CLI shows their dispositions and counters. The teacher queries for their unique markers and gets zero retained rows. Switch to a denied app and pause the session to demonstrate capture stops. Forget one kept note, verify after restart and retrieve an unrelated kept note.

## Capture and admission contract

- File permissions, screen-window permission and permission to send kept text to Supabase are separate choices. Approve exact apps, windows and documents for this session. Use fictional demo content. Default to stopped. Provide visible recording state, pause, resume and stop. Restart requires a new session.
- For the macOS capture spike, try ScreenCaptureKit window selection with local Vision OCR. Verify permission denial, app identity, window closure, focus changes, overlays and revoked permission on the presentation Mac. Capture only the approved foreground window. Discard in-flight results when focus, window identity or permission changes. Keep raw frames and unapproved OCR in memory only. Exclude the terminal database feed to prevent capture loops.
- Convert each changed passage to a self-contained candidate with explicit same-source context. Suppress unchanged frames and repeated saves. For the same document seen through two routes, link the evidence or deduplicate the candidate. Preserve genuine changes as versions. Never infer history from unrelated rows.
- Apply privacy checks before scoring or transmitting text. The admission MLP is a preview score only (decided 16 Nov): it never gates saving. In the approved auto-save session a note is written only when local Qwen extracts an exact quote that passes validation, and acknowledgments and short unresolved-reference quotes are dropped by a deterministic filter. Blocked input or a cloud outage must visibly stop or fail the write. Keep rejected text out of logs, retries, indexes and cloud tables. Demo observations are inference inputs only.
- Use the existing Drive/Supabase ownership, versioning, citations, tombstones and receipts. Extend the storage contract for screen and app identities before wiring these routes. Today the cloud RPC expects a Drive file ID. Verify owner isolation, stable observation IDs, retry idempotency and deletion of all derived text. SQLite remains useful for offline development. Hosted database evidence is required at rehearsal.
- Proposed CLI interaction: start a session, approve sources, watch events, inspect a decision, query saved notes, pause, resume, forget and stop. Show concise errors and distinguish captured, rejected, pending and committed events. A direct read-only database query supplies independent proof of persistence.

## Work calendar and supervisor decisions

Dates are targets in Asia/Kolkata. AI handles implementation, fixtures, automated checks and reproducible run instructions in parallel where interfaces allow. The supervisor selects sources, grants OS/account access, reviews expected decisions and signs off observed behavior on the Mac. Each checkpoint ends with something runnable.

| Dates | AI development | Supervisor checkpoint and exit evidence |
|---|---|---|
| 10–11 Nov | Define a common observation record and CLI session controls. Spike one document change, one approved-window OCR read and one hosted C2 write separately. Start bounded MLP selection in parallel. | Select two apps and optional third, demo documents, account and exact window. Grant permissions locally. Verify the OCR-only marker and signed-in database access. |
| 12–13 Nov | Connect the first app and screen route through policy and admission to a committed row. Build the read-only terminal database view. Add pause and stop. | Watch a new sentence reach the hosted database. Switch apps mid-capture and inspect the negative result. |
| 14–16 Nov | Add second app, Drive version polling if chosen, deduplication, event provenance and retry handling. Freeze development-selected model and thresholds. | Show one kept note per required app, an unsaved screen-only keep, one skip, one abstention and one privacy rejection. Query the database independently. |
| 17–19 Nov | Run labeled fictional replays and fresh on-screen scenarios. Check source attribution, latency, version updates, retrieval, forgetting, network interruption and permission revocation. Add third app once two pass. | Review expected vs actual decisions, mistakes and all privacy failures. Repeat the same workflow after restarting the CLI. |
| 20–21 Nov | Fix failures, run regressions, freeze dependencies, model, thresholds and CLI release. Prepare a repeatable fixture set and read-only audit queries. | Approve the release on the actual presentation Mac. Drop optional generation and third-app polish first if time slips. |
| 22–23 Nov | Rehearse with fresh credentials and fresh fictional markers on 22 Nov. Present the frozen build on 23 Nov. | Record which apps, routes and database writes worked live. A failed hosted write or denied-window leak leaves that gate open. |

## Evidence and release gates

- Stage A is signed off. The exploratory admission dataset has 1,584 reviewed rows. Its 96 uncertain actions retain null binary targets. Pre-training checks and five validation baselines are complete. MLP comparison and integration are pending. See the [stage log](../reports/session_log.md) and [baseline results](../reports/admission_baselines_v1/report.json).
- Preserve the [Stage D protocol](NeuroBrain_Session_Plan.md): at most four MLP configurations, three seeds for the selected configuration, validation-only selection, then one frozen final test. The 48 known final targets and 12 final ambiguity probes stay reserved. Keep suggestion mode for general use. Session-scoped automatic writes are a supervised demo on fictional inputs.
- Build a separate, supervisor-reviewed demo fixture table with source, presented text, expected decision and expected database effect. Include useful updates, irrelevant acknowledgments, clear and missing referents, explicit privacy directives, repeated frames and an overlapping file/screen observation. The app receives candidate text and permitted context only. Expected labels and fixture IDs stay in the test harness. Report observed decisions, counts and errors separately for native and OCR input.
- Measure change-to-commit time for each route. Target a visible write within five seconds for a short local demo note on the presentation network. Show the actual times and retry a disconnected write without duplicating it. Check zero forbidden markers across the database, indexes and application logs. Test another signed-in user cannot see the rows.
- C2 already has a CLI and a PostgreSQL-tested lifecycle. Hosted auth, screen capture, automatic admission and live multi-app writes each need end-to-end evidence. Follow [Cloud Setup](Cloud_Setup.md) for the Drive lifecycle and credentials. Only eligible, committed notes appear in the teacher’s database feed.
- Run the existing offline regression suite plus the cloud SQL fixture and new capture/admission tests. Repeat the live walkthrough from a fresh CLI process on the presentation Mac. Synthetic inputs and mocked capture cover regression cases. The supervisor records the real window permissions, source switches and hosted writes during rehearsal.

**First milestone:** on the presentation Mac, take one explicitly approved live window through local OCR and display a new unsaved fictional marker in the terminal. In parallel, verify one real signed-in Supabase write and start the MLP comparison. Join these paths before expanding app coverage.
