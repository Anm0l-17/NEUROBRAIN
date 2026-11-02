# NeuroBrain

NeuroBrain is a local notes-memory assistant. It helps a user import selected notes, find useful evidence, see where that evidence came from, and deliberately forget a saved source.

## Current status

The first working prototype is complete for fictional Markdown and TXT notes. It includes:

- local note import and version history
- search with exact source excerpts and citations
- a small command-line interface and local browser interface
- source-scoped deletion with verification
- privacy checks for unsupported, hidden, oversized and obvious credential-containing notes

The prototype is not yet a finished research system. Semantic search, generated answers, temporal facts, cloud sync and automatic neural memory filtering are future stages. The admission-model pilot is an isolated experiment and does not control real note storage.

## Try the prototype

From the project directory:

```bash
PYTHONPATH=src python3 scripts/demo.py
```

For the browser version:

```bash
PYTHONPATH=src python3 -m neurobrain import examples/notes/project.md
PYTHONPATH=src python3 -m neurobrain import examples/notes/preferences.txt
PYTHONPATH=src python3 -m neurobrain serve
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765). The example notes are fictional.

## Project direction

The next prototype stage moves original note files to a selected Google Drive folder and uses Supabase PostgreSQL for searchable evidence, citations, versions and deletion records. The current SQLite implementation remains the tested local reference until the cloud version reaches feature parity.

See the [cloud setup guide](docs/Cloud_Setup.md), [system design](docs/System_Design_v0.1.md), [working plan](docs/NeuroBrain_Working_Plan.md), [full session plan](docs/NeuroBrain_Session_Plan.md), and [verification report](reports/verification.md).

## Privacy boundary

Only explicitly selected TXT/Markdown notes are accepted by the current prototype. Original files are not deleted when saved memory is forgotten. Deletion removes the selected source from the application database and search index, but it does not erase backups, copied text, browser history, or old database copies. This is application-level deletion, not forensic erasure or model unlearning.

The current local prototype does not upload notes or use them for training.
