# Prototype v0.1 verification

**Executed:** 27 October 2026. **Environment:** macOS ARM64, Python 3.13.1, SQLite 3.45.3 with FTS5. Application runtime dependencies: none beyond Python/SQLite. Development tool versions are recorded in `requirements-dev.txt`.

## Executed gates

| Gate | Result | Evidence |
|---|---|---|
| Regression suite | PASS | `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v`: **15/15 tests passed**, final run 0.598 seconds |
| Lint | PASS | `.venv/bin/ruff check src tests scripts`: all checks passed |
| Formatting | PASS | `.venv/bin/ruff format --check src tests scripts`: eight files already formatted |
| Compilation | PASS | `.venv/bin/python -m compileall -q src tests scripts` |
| Package build | PASS | Wheel built with `pip wheel --no-build-isolation --no-deps --wheel-dir dist .` |
| Local install | PASS | Installed package and `neurobrain --help` command worked |
| Clean environment | PASS | Fresh temporary venv; wheel installed using `--no-index --no-deps`; imported fixture, searched SQLite, checked packaged HTML resource; temp environment removed |
| Repeatable demo | PASS | `PYTHONPATH=src .venv/bin/python scripts/demo.py`: all eight steps passed, including store restart and reimport suppression |
| Browser walkthrough | PASS, scoped | Opened real browser; searched SQLite and saw cited source lines; previewed and confirmed deletion; repeated search returned no evidence; retained source remained listed; fresh demo duplicate import and inspection worked |
| Browser rendering | PASS, desktop only | Inspected page screenshot and accessibility snapshot; forms, source cards and exact evidence rendered. No console warnings/errors after fresh page reload |
| Code/security review | Scoped check | No external service client or model call; note rendering uses `textContent`; credential matches in code scan were the policy expression and fictional test fixture. This is not a comprehensive security audit |
| Static types / coverage | NOT MEASURED | No static type checker or coverage tool was run; do not infer coverage percentage from test count |
| Source-control diff | UNAVAILABLE | Project directory is not a Git repository; no commit or diff verification claimed |

Wheel artifact: `dist/neurobrain-0.1.0-py3-none-any.whl`, SHA-256 `cfefce073ada9fd2eef31782770800402c048eeaf09b25c5e4bd54124c95a6e8`.

## What the tests cover

- Duplicate import idempotency and persistent evidence after restart.
- Bounded chunks, exact Unicode character spans, line starts, and long single-line handling.
- Edited source versions: history retained, only current version searched.
- Forget every version of the selected source, verify FTS terms disappear, preserve unrelated content and original files, restart, block identical reimport including renamed copies.
- Stale deletion preview rejection.
- Simulated import failure rolls back active-version changes and index writes.
- Simulated receipt failure rolls back deletion, index changes and tombstones.
- Rejected oversized, hidden, unsupported, empty, binary, credential-pattern, do-not-store, malformed UTF-8 and missing notes persist no source text.
- Directory exclusions, symbolic-link rejection, and query-time notes-root filtering.
- Caller-supplied FTS punctuation is treated as literal tokens; absent evidence returns a controlled result.
- Foreign keys and external-content FTS integrity.
- CLI lifecycle and controlled errors; HTTP/CLI evidence parity.
- Local HTTP mutation token, origin and host checks; traversal rejection; no-store headers.

Initial HTTP tests could not bind localhost under the default execution restrictions. The run with additional loopback permission completed successfully; this was an environment restriction, not a skipped test. Build operations showed a pip-cache permission warning; caching was disabled and the build/install succeeded.

## Limits and release decision

**Ready for a basic system-design and implementation demonstration using fictional notes. Not a completed research release.**

Not tested or implemented: neural training/accuracy, embeddings, semantic/hybrid retrieval, temporal truth, generation correctness, held-out QA benchmarks, 10k-chunk performance, mobile/browser compatibility matrix, network-blocked offline test, hostile concurrent filesystem substitution, old-backup restore suppression, model/cache/summary deletion, or forensic erasure. No guarantee about these follows from the 15 development tests.

## Self-evaluation

Using the agent-self-evaluation skill; evaluation applies to this first checkpoint, not the entire 60-session project.

| Axis | Score | Evidence and next improvement |
|---|---:|---|
| Accuracy | 4 | Executed lifecycle, build, install and browser checks; no measured semantic QA or trained model claims. Add retrieval evaluation on a reviewed corpus next. |
| Completeness | 4 | Runnable basic memory modules plus design, demo and session mapping; full proposed neural modules remain future work and are explicitly labeled. Review professor's module expectations at the next checkpoint. |
| Clarity | 4 | Current and proposed architectures are separated; extensive reference documents need a rehearsed five-minute explanation. |
| Actionability | 4 | Running fictional demo, copyable commands, installable wheel and repeatable script; model/hardware feasibility remains a prerequisite for training. |
| Conciseness | 4 | Final handoff can link to durable artifacts; privacy and status details intentionally recur across independently usable documents. |

Overall: **4.0/5**. Highest-impact improvements: (1) student review/rehearsal against the actual presentation date, (2) model/hardware trial and reviewed 80-example admission pilot, (3) ten-note retrieval corpus and embedding baseline. Self-check: the user can demonstrate real working modules now, while the neural research contribution remains visibly unfinished.
