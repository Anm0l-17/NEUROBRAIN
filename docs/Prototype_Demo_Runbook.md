# Mentor prototype run sheet — 23 November 2026

Use fictional content only. Rehearse on 22 November on the presentation Mac.
The full milestone requires Notion, saved-file and approved-window input plus
hosted evidence. The tested local walkthrough below is a fallback, not proof of
those live gates. Record actual outcomes beside the fixture table.

## Before presenting

1. Run the local regression suite and check the latest overnight handoff.
2. Start Ollama. Run the disposable walkthrough once to expose cold-start/runtime
   failures before the audience arrives. Do not increase timeouts to hide failures.
3. Use a fresh fictional database for rehearsal; never remove existing tombstones
   to make forgotten content reappear. Preserve original files.
4. For Open WebUI, select `neurobrain-memory` and verify its connection to the same
   database as the observer. `neurobrain-test` is general chat without memory.
5. For the full demo, independently verify hosted sign-in, source permissions,
   recording permission and the approved foreground window. Renew credentials
   locally; never place them in slides, command history or this report.

## Five-minute explanation and local walkthrough

| Time | Action | What to say/show |
|---|---|---|
| 0:00–0:40 | Show problem and architecture | Selected input → policy → exact supported notes → versioned memory → cited recall → explicit forgetting. |
| 0:40–1:10 | Explain the models | MiniLM and Qwen are pretrained; only the small experimental admission MLP was trained. Its preview scores do not govern saving. |
| 1:10–2:30 | Run the model-backed walkthrough | Show saved notes, citations, duplicate suppression and the changed date. |
| 2:30–3:30 | Show no-evidence and forgetting | Verify after reopening; retain the unrelated preference; show tombstone rejection. |
| 3:30–4:20 | Show source provenance/UI | Observation reference, route, version, evidence span and deletion preview. |
| 4:20–5:00 | State results and open gates | Development checks passed; broad accuracy, live two-app capture and hosted acceptance need separate evidence. |

From the repository root:

```sh
PYTHONPATH=src .venv/bin/python scripts/demo_observation.py
```

The script uses real local Qwen with a disposable SQLite store. It exits on a
failed assertion or request and prints success only after the whole path passes.
It changes the fictional date from 23 to 24 November solely to demonstrate
versioning; the actual presentation deadline remains 23 November.

If the model is unavailable, use the deterministic demonstration and label it:

```sh
PYTHONPATH=src .venv/bin/python scripts/demo.py
```

Do not present a model-free fallback as a completed model-backed run.

## Supervised acceptance fixtures

Run each fixture through the named approved input. Expected decisions belong in
the test sheet, never in the candidate text passed to the model. The supervisor
must review this draft table before treating it as acceptance evidence.

| ID | Route and fictional input/action | Expected result | Evidence to record |
|---|---|---|---|
| F01 | Notion: “The violet demonstration is on 23 November 2026.” | Supported milestone retained after explicit save | Source, route, exact span, acknowledged row, elapsed time |
| F02 | Saved Markdown: “Mira prefers concise answers with references.” | Supported preference retained | File reference, version, evidence ID |
| F03 | VS Code Auto Save off: “The amber rehearsal room is Cedar 417.” | Screen-only fact available before saving file | Window identity/session, OCR text span, query result |
| F04 | Save F03 to the corresponding file | One logical observation, linked routes | **Cross-route merge currently pending**; record actual duplicates |
| F05 | Replace F01 date with 24 November | New version; current answer uses 24 | Both versions inspectable, current citation |
| F06 | “Okay, thanks.” | No useful retained excerpt | Actual extraction, absence of phrase in active chunks |
| F07 | “Move that to there after the thing is finished.” | Abstain/review; no automatic useful-memory claim | **Known model ambiguity risk**; record any false keep |
| F08 | `neurobrain: do-not-store` followed by a unique fictional marker | Rejected before model inference/persistence | No marker in retained chunks, indexes or application logs |
| F09 | Ask an unrelated nonexistent fact | No evidence | Exact response and stored search result |
| F10 | Switch to denied foreground app, pause, then stop | No subsequent capture/save | Visible state, observation count and negative database query |
| F11 | Forget F01 and reopen | All versions unavailable; F02 retained | Receipt, fresh-process queries and original source intact |
| F12 | Disconnect during hosted write, reconnect/retry | No false “saved”; no duplicate commit | Error, acknowledgment and independent hosted query |
| F13 | Query hosted rows as another demo user | No access to first user's evidence | Separate user identity and empty/denied result |

Live screen tests also cover closed windows, overlays, revoked permission and
focus changes during inference. The selected-file route observes saved bytes;
it does not prove which application wrote them. An empty saved extraction creates
an empty current version, with old evidence retained only in history.

## Hosted acceptance gate

The existing `cloud` command and `supabase/c2.sql` implement a Drive lifecycle.
They do not yet transport Notion/window observations. Before claiming the full
milestone, implement/test that provenance contract, then show an acknowledged
signed-in write, an independent hosted query, retry idempotency and deletion.
Follow [Cloud Setup](Cloud_Setup.md) for the existing Drive demonstration.

Record run date, build/model identifiers, fixture IDs, expected/actual results,
route latency, failures and supervisor sign-off. Source-change-to-commit target
is five seconds; report actual values even when slower. Saved model answers in
Open WebUI history and network/client buffers are outside NeuroBrain deletion.

## Claims to avoid

- “60% complete” is a readiness estimate, not accuracy.
- A perfect small fictional fixture run is not broad generalization.
- Exact quoted text does not establish its usefulness or resolve ambiguity.
- MLP validation did not establish improvement over the logistic baseline.
- Local/mocked checks do not prove hosted ownership or real screen permissions.
- A pretrained Qwen alias with prompt settings is not a fine-tuned new model.
