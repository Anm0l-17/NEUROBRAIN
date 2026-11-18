# First live observation checks

## Repeatable local evidence demo · 13 November

With Ollama running, execute `PYTHONPATH=src .venv/bin/python scripts/demo_observation.py`
from the repository root. It uses fictional notes and removes its temporary database.
Assertions check extraction, duplicate suppression, restart, cited answers, a changed
date, absent evidence, all-version forgetting, retained unrelated evidence and
tombstone rejection. It prints JSON only after all checks pass. A failed request
or assertion means the walkthrough did not pass; do not use a partial run as evidence.
Two development runs passed in about 5.1 seconds on 13 November after restricting
model citation output to retrieved IDs. These are small local smoke checks, not a
general accuracy or latency benchmark. An earlier 60-second timeout remains recorded.

Observation listings now include the source reference and capture route alongside
the storage identifier. Re-extracting the same input with changed supported quotes
creates a new version; repeating the same extraction stays idempotent.
An explicitly saved snapshot with no extracted notes becomes an empty current
version: old quotes remain inspectable in history but disappear from current
search. This prevents stale facts surviving a source replacement. Empty output is
not an uncertainty score or a reviewed abstention; inspect model output before
using automatic saving on anything beyond the fictional supervised demo.

## Ask from Open WebUI

The local bridge exposes `neurobrain-memory`, which searches the observation
database and returns cited excerpts selected by pretrained Qwen3.5. It does not
fine-tune Qwen. Keep Ollama running and first save notes using the commands below.
Start the bridge in a separate terminal:

```zsh
cd "/Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN"
export NEUROBRAIN_CHAT_KEY="$(.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')"
print -rn -- "$NEUROBRAIN_CHAT_KEY" | pbcopy
PYTHONPATH=src:. .venv/bin/python -m neurobrain.chat_api
```

The generated key is on the clipboard. In your private Open WebUI instance,
open Settings > Admin > Connections and add an OpenAI-compatible connection:

- URL: `http://127.0.0.1:8766/v1`
- API key: paste the generated key.
- Verify the connection, save, and select `neurobrain-memory` in a new chat.

These are the provider fields described in the
[official Open WebUI guide](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/).
The URL assumes Open WebUI's backend runs directly on the same Mac. A container
or remote backend needs separate connectivity verification; do not expose this
single-user bridge publicly. Anyone with this connection can query the configured
notes database. Use a private instance and fictional notes for the demo.

Ask complete questions such as “When is the prototype demonstration?” The bridge
uses the last question only, so follow-ups such as “What about that?” do not carry
conversation context. It supports text questions, model discovery and streamed
response framing; it does not support tools or image uploads. The whole answer
arrives after evidence selection finishes. Source markup is displayed literally.

Questions containing referential words such as “it”, “its”, “that” or “their” are
conservatively rejected with a request to name the subject. Rephrase with the
explicit project/person name. This guard can reject otherwise understandable
questions and is not full reference resolution. During final answer delivery the
bridge holds a short database write transaction and rechecks evidence: deletion
cannot commit between that check and the socket write. An already-delivered answer
or bytes buffered by the client/network remain outside the deletion boundary.

The default database is `.neurobrain/observations.sqlite3` and default notes root
is `examples/notes`; these must match the observer. Use `--db` and `--notes-root`
when changing them. Stop with Ctrl-C. A new generated key requires updating the
connection. The separate Ollama alias `neurobrain-test` does not query this database.

Forgetting a source removes it from subsequent NeuroBrain answers. It does not
erase answers already copied into Open WebUI's chat history; delete those chats
there separately. Actual Open WebUI rendering remains a live acceptance check.

Verified on 11 November: real local Qwen extracted a fictional dated milestone,
the HTTP chat endpoint returned it with its stored citation, and the same question
returned no evidence after forgetting the source. The temporary database was
removed afterward. All 53 Python regression tests passed, including authentication,
model discovery, streaming framing, deletion and literal source-markup checks.

## Approved-window ingestion · 11 November

Build the helper as shown below. Open a dedicated VS Code window containing only
fictional content, hide unrelated sidebars and turn off Auto Save. Use its exact
window title with the new source option:

```zsh
cd "/Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN"
PYTHONPATH=src:. .venv/bin/python -m neurobrain.observe --screen-title 'EXACT WINDOW TITLE' --save-extracted
```

Switch to the selected window within five seconds. Capture is limited to that
foreground VS Code window. The CLI checks its identity after OCR and again after
Qwen inference before writing. Frames remain in memory. The policy checks all
recognized text before extraction. A denied or changed window aborts the operation.
Use `--extract` instead of `--save-extracted` for an extraction preview.
Add `--watch` for an explicitly started five-minute session.

Query the same observation database with the answer command below. The live
acceptance check is finding a new fictional fact before saving the editor file,
then verifying that a denied foreground app produces no retained evidence.
The current implementation supports VS Code screen capture. Notion uses the
approved-page reader. Cross-route duplicate merging remains pending.

## Structured extraction, storage and questions · 11 November

From any Terminal directory, run this command to extract and save permitted
quotes from the fictional file. Qwen selects the quotes. Their kind remains a
model prediction. The application verifies their exact source spans before saving.

```zsh
cd "/Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN" && PYTHONPATH=src:. .venv/bin/python -m neurobrain.observe --file examples/notes/project.md --save-extracted
```

Add `--watch` for the five-minute session and enter `start`. To use the approved
Notion page, replace `--file examples/notes/project.md` with `--notion-page PAGE_UUID`
after setting the local token as described below.

The following commands query the same local observation database:

```zsh
PYTHONPATH=src:. .venv/bin/python -m neurobrain --db .neurobrain/observations.sqlite3 sources
PYTHONPATH=src:. .venv/bin/python -m neurobrain --db .neurobrain/observations.sqlite3 answer "When is the demo?"
PYTHONPATH=src:. .venv/bin/python -m neurobrain --db .neurobrain/observations.sqlite3 inspect SOURCE_ID
```

Answers consist of source quotes selected by Qwen, with validated citation IDs.
An empty answer means the retrieved evidence did not support the question.
Use the existing `forget SOURCE_ID --preview` and `--confirm PREVIEW_TOKEN`
commands with the same database and notes root to remove every version.
The original file or Notion page remains under the owner's control.

Extraction still needs review before unattended use. In the 11 November
developer-authored smoke checks, Qwen retained an ambiguous instruction as a
preference. Stronger wording, contrasting prompt examples and a separate
yes/no context check did not reliably reject it. Enabling reasoning made the
original error persist and several requests reach the 60-second timeout. Those
experiments are recorded in `reports/extraction_smoke_2026_11_11.json`,
`reports/extraction_context_smoke_2026_11_11.json`,
`reports/extraction_examples_smoke_2026_11_11.json` and
`reports/extraction_reasoning_smoke_2026_11_11.json`. The active fast prompt is
unchanged. Exact quote checks prevent invented text but cannot establish that a
real quote is useful or unambiguous. Inspect notes before relying on them.

Verified with fictional text on 11 November: extraction and storage of two notes,
cited date answer in a fresh store connection, all-version deletion and absence
after reopening. Hosted persistence and live screen ingestion remain pending.

Run from the project root on the presentation Mac. Use a fictional demo file and a separate fictional Notion page.

## Watch a selected file

```zsh
export PYTHONPATH=src:.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
.venv/bin/python -m neurobrain.observe --file examples/notes/project.md --watch --checkpoint models/admission-grid-nov10/lr0.001-drop0.2-seed17/checkpoint.pt
```

Enter **start**, save a change in the selected Markdown file, then try **pause**, **resume**, and **stop**. The monitor polls every two seconds and expires after five minutes. A changed snapshot prints a count and optionally one local usefulness score per nonblank line. Each line is scored independently with empty prior context. The file reader observes saved bytes and cannot identify which editor wrote them. Automatic saving awaits evaluation of abstention on demo inputs.

## Read the selected Notion page

Grant a read-only internal Notion connection access to one flat demo page. Use plain text paragraphs, headings, lists, quotes or to-dos. Set the token in your own terminal using the hidden prompt. Use the page UUID from the page URL.

```zsh
read -rs 'NEUROBRAIN_NOTION_TOKEN?Notion token: '; echo
export NEUROBRAIN_NOTION_TOKEN
.venv/bin/python -m neurobrain.observe --notion-page YOUR_PAGE_UUID --watch
```

## Test the unsaved screen marker

Open only fictional content in a dedicated VS Code window, hide sidebars, turn off Auto Save, and type a distinctive marker into the editor. Copy its exact window title. In macOS Privacy & Security, authorize the terminal or capture helper if needed. Run:

```zsh
mkdir -p .neurobrain
swiftc -parse-as-library -module-cache-path .neurobrain/swift-cache scripts/window_probe.swift -o .neurobrain/window-probe
.neurobrain/window-probe 'EXACT VS CODE WINDOW TITLE' 'your fictional marker'
```

Switch back to that window within five seconds. The one-shot probe captures only the selected titled VS Code window, checks foreground identity before and after capture/OCR, and reports whether the marker appeared. Frames and recognized text stay in memory. Repeat with another app in front and check that capture stops. The probe is separate from the supervised file/page monitor.

## 10 November verification

The saved-file CLI, interactive controls, offline MLP inference and synthetic Apple Vision marker check ran locally. The selected seed-17 checkpoint (learning rate 0.001, dropout 0.2) reloaded with zero prediction difference. Across four configurations the best validation average precision was 0.7755 on 18 rows. Repeats of that configuration gave 0.7615 (seed 42) and 0.7754 (seed 101). The embedding logistic baseline reached 0.8674. All six MLP runs achieved F1 0.8571. Final test rows remain reserved.

Live Notion access, the actual approved-window switch tests and a signed-in hosted write require the supervisor's demo sources and local permissions. The database lifecycle instructions are in [Cloud Setup](Cloud_Setup.md).
