# NeuroBrain

A local notes-memory assistant. **First implementation checkpoint: 27 October 2026.**

This prototype imports selected Markdown/TXT notes, stores versioned evidence, searches it locally, shows exact cited excerpts, and forgets all imported versions of a selected source. CLI and web share the same services. It has **no runtime dependencies beyond Python 3.11+ and SQLite with FTS5**.

An isolated fictional-data admission training pilot is available; see the [29 October pilot report](reports/admission_pilot_2026-10-29.md). It is not integrated into the application and must not discard real notes. Embeddings in the application, hybrid search, temporal facts, and language-model generation are **not implemented yet**. The latest [session plan](docs/NeuroBrain_Session_Plan.md) remains the research schedule. This checkpoint brings forward part of its deterministic baseline to support the professor's system-design and basic-implementation presentation.

## Run now

From the project directory:

```bash
cd /Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN
PYTHONPATH=src python3 -m neurobrain import examples/notes/project.md
PYTHONPATH=src python3 -m neurobrain import examples/notes/preferences.txt
PYTHONPATH=src python3 -m neurobrain serve
```

Open **http://127.0.0.1:8765**. Search `SQLite` or `Mira`, inspect a source, and preview deletion. Stop with Ctrl+C. For a repeatable demo that does not modify your saved memory:

```bash
PYTHONPATH=src python3 scripts/demo.py
```

Default database: `.neurobrain/memory.sqlite3`. Default allowed notes folder: `examples/notes`. These paths are relative to the directory where you run the command. To use your own selected folder:

```bash
PYTHONPATH=src python3 -m neurobrain --notes-root /absolute/path/to/notes --db .neurobrain/personal.sqlite3 serve
```

Enter a filename relative to the allowed notes folder in the web import form. Use a separate database for separate projects. Imported text is stored as a snapshot: editing or removing an original file does not automatically change saved memory. Reimport to create a new version; forget to remove saved versions.

## CLI

```bash
PYTHONPATH=src python3 -m neurobrain policy
PYTHONPATH=src python3 -m neurobrain sources
PYTHONPATH=src python3 -m neurobrain search 'SQLite'
PYTHONPATH=src python3 -m neurobrain ask 'SQLite'
PYTHONPATH=src python3 -m neurobrain inspect SOURCE_ID
PYTHONPATH=src python3 -m neurobrain forget SOURCE_ID --preview
PYTHONPATH=src python3 -m neurobrain forget SOURCE_ID --confirm PREVIEW_TOKEN
```

Replace `SOURCE_ID` and `PREVIEW_TOKEN` with the values returned by the preceding commands. `ask` currently returns matching excerpts, not a synthesized answer. Empty retrieval returns an explicit no-evidence response. A lexical match alone is not evidence of answer correctness.

## Privacy and deletion boundary

- Only explicitly selected TXT/MD files inside the allowed directory are accepted. Hidden/excluded paths, symlinks, malformed UTF-8, binary/empty input, and files over 1 MiB are rejected before their content is persisted.
- A line beginning `neurobrain: do-not-store` rejects the whole note. The same directive can appear at the start of an HTML-comment line. Credential-pattern checks are conservative heuristics, **not comprehensive secret detection**. Inspect notes yourself before import.
- Forget removes every imported version of the selected path, its chunks, and FTS entries transactionally. A stale preview is refused. Content-free receipts and SHA-256 tombstones remain; identical forgotten text cannot be accidentally reimported, including from a copied file. Changed text is a new input and is not blocked by that fingerprint.
- Other separately imported sources remain, even if they contain overlapping information. Deletion is source-scoped, not a semantic purge across every note. Original files, backups, old database copies, browser/process memory, and previously copied/displayed answers are outside this boundary. Restoring an older database also restores its old tombstone state; restore suppression is future work.
- SQLite `secure_delete` is enabled, but this is application-level deletion, **not forensic disk erasure or model unlearning**. There are no vectors, summaries, generation caches, or trained models in this milestone.
- The web server binds only to loopback and checks host, origin and a per-launch request token. It is a single-user demonstration server. Local memory is **not encrypted** by this application. No notes are uploaded, logged, or used for training.

## Verify and install

The complete standard-library test suite needs no pytest installation:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

HTTP tests need permission to bind a temporary loopback port. Packaging/lint tools are optional development dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/python -m pip wheel --no-build-isolation --no-deps --wheel-dir dist .
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/neurobrain --help
```

See [system design](docs/System_Design_v0.1.md), [professor demo guide](docs/Presentation_Checkpoint.md), [verification evidence](reports/verification.md), and [session log](reports/session_log.md).
