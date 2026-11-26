# Finish plan: everything by 30 Nov 2026

Work goes on branch `claude/finish-nov30`, cut from `claude/evidence-selector-training` at `458fbf0` (26 Nov). The running
prototype (port 8766) runs from the `prototype-remaining-work-c15a7d` worktree and must **not be touched**: no edits
there, no restart, no writes to the live DB at `/Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN/.neurobrain/observations.sqlite3`.
Read the live DB only via `sqlite3 -readonly "file:...?mode=ro" ".backup <scratch copy>"`.
Everything lands on the new branch and goes to `main` in one PR at the end (F3), only once the user says yes.

Owners: **C** = Claude; **U** = only the user can do it; **C+U** = Claude prepares, user runs or approves.

## Where things stand (26 Nov evening)

| Area | State | Evidence |
|---|---|---|
| Selector v2 | Passed sealed gate; live in the prototype | `reports/selector_v2/README.md` |
| Selector v3 (prefers the newest fact) | Data, gate and notebook ready; **not trained** | branch `claude/selector-v3-update-rows` (`reports/selector_v3/README.md` there; gate items 1–9) |
| Extraction | Windowed and verified; keeps 14 of ~16 page facts | commit `808cf28`; `reports/live_check/README.md` |
| Retrieval | FTS5 + porter stemming + stopwords + next note; misses cause/effect wording | `reports/retrieval_v1/README.md`, `core.py:382-430` |
| Live check | v2 15/20, base Qwen 12/20 (v2 misses: 3 stale-fact, 1 search, 1 arguable) | `reports/live_check/` |
| Hosted, OCR, Notion, deletion | Passed 24 Nov live gates; limits recorded | `reports/demo_week/2026-11-24-hosted.md` |
| Generator LoRA, admission MLP | Negative or advisory results | `docs/Generator_Training_Readiness.md`, `reports/admission_v2/` |
| Docs | Stale: no selector v2, retrieval v1 or windowing; session log stops 16 Nov; `System_Design_v0.1.md:131` says cloud is "planned"; `Prototype_23_November_Plan.md:5` says fine-tuning deferred; `NEUROBRAIN.md:89` has an empty heading | search report |
| Final report, slides, model cards | **Do not exist**. `ResearchPaper.md` is only the 16 Oct literature review (identical to `NeuroBrain_22_Paper_Literature_Review.md`) | |
| Tests | 96 pass outside hidden folders; `tests/test_observe.py:14` puts its temp folder under the cwd, and `observe.py:136-140` rejects any hidden ancestor, so it fails inside `.claude/worktrees` | |
| PRs | #3 open (stale, head `claude/prototype-remaining-work-c15a7d`); `main` is 63 commits behind | |

## A. Models
| # | Task | Owner | Done when |
|---|---|---|---|
| A1 | Kaggle v3 training: smoke run, then full (~2 h 55 m). Steps are in the v3 README | U | `adapter.zip` downloaded |
| A2 | Deploy v3 (`scripts/deploy_selector.sh` as `neurobrain-selector-v3`); score both sealed files against the 9-item gate | C | Gate table filled in |
| A3 | Merge `claude/selector-v3-update-rows` into this branch (always: data and report). Make v3 the app default **only if** every gate item passes | C | |
| A4 | Re-run `reports/live_check/score.py` (unchanged) with base, v2 and v3 on a fresh read-only copy of the live DB | C | Dated JSON and table |
| A5 | No more generator or admission training; write up the negative results honestly | C | In E1 |

If v3 fails, v2 stays and v3 is reported as a negative result. Nothing else waits on v3.

## B. Code fixes (measure before and after; never weaken the exact-quote check or `import_observation`'s re-verification)
| # | Task | Done when |
|---|---|---|
| B1 | Extraction recall: find why "Priya Raman founded it in 2023 and still picks the books…" and "Rosa … 10% off drinks" are dropped (model omission? window cut? `unresolved_quote`? dedupe?), then fix in `extract.py` | Retyped book club page stores both; regression tests; `reports/retrieval_v1/run.py` and live check do not regress |
| B2 | Cause/effect retrieval: try `semantic.hybrid_search` (RRF with MiniLM, exists in `semantic.py:179`) inside `answer()` behind `NEUROBRAIN_HYBRID=1`, with lexical fallback if the encoder is missing | Measured on the retrieval fixture + live check. "Why did the venue change?" found, no regressions. Default on only if strictly better |
| B3 | `tests/test_observe.py` temp-folder bug (fix the test, not the hidden-path policy) | All tests pass inside `.claude/worktrees/...` |
| B4 | `reports/live_check/README.md` cites `reports/selector_v3`, which only exists after A3 | Correct after A3 |
| B5 | `scripts/start_prototype.sh`: selector model from `NEUROBRAIN_SELECTOR_MODEL`, defaulting to the promoted model | |

Out of scope, written up as future work: generator fine-tuning, Titans/Mamba, unlearning, skill synthesis
(`docs/NeuroBrain_Working_Plan.md:37`), forensic deletion, per-passage forget, real network-drop test (F12),
screen pause/stop and revoked-permission tests.

## C. Evaluation
| # | Task | Owner |
|---|---|---|
| C1 | Full test suite on the final branch; record the count | C |
| C2 | `reports/Final_Evaluation_2026-11.md`: one table with the sealed gates (base, v1, v2, v3), retrieval fixture, live check (base/v2/v3), 24 Nov hosted/OCR/Notion gates, extraction fact recall, and test count. Every number cites its raw file | C |
| C3 | Dress rehearsal on the **presentation Mac** with the updated runbook; save a dated note in `reports/demo_week/` | U (C writes the checklist) |
| C4 | Backup demo video | U |

## D. Documentation
| # | Task |
|---|---|
| D1 | README: current pipeline, one-command start, selector, retrieval, honest limits |
| D2 | `reports/session_log.md`: entries for 17–30 Nov |
| D3 | `docs/Prototype_Demo_Runbook.md`: chat key, pick `neurobrain-memory` in Open WebUI (not the raw Ollama model, which uses Open WebUI's calendar tools), one Notion page per topic, demo questions with expected answers, known misses |
| D4 | Stale lines: `System_Design_v0.1.md:131`, `Prototype_23_November_Plan.md:5`, `NEUROBRAIN.md:89`, first-release scope (`NEUROBRAIN.md:17-18` vs `Working_Plan.md:37`) |
| D5 | Update `docs/NeuroBrain_Architecture.mmd` to the current pipeline |
| D6 | Model and data cards: selector v2/v3, selector data v2/v3, admission data |

## E. Final deliverables
| # | Task | Owner |
|---|---|---|
| E0 | Confirm what the college wants on 30 Nov: report template, page limit, slides, viva or demo date, how code is submitted | U |
| E1 | `docs/Final_Report.md`: abstract, problem, related work (condensed from the 22-paper review), design, data, training (selector v1→v2→v3 with gates; generator and admission negatives), evaluation (from C2), limits, future work, references. Every number traceable to C2 | C |
| E2 | Slide deck (~12 slides) plus a demo script | C |
| E3 | Export to the required format (PDF/DOCX/PPTX) | C+U |

## F. Integration and safety
| # | Task | Owner |
|---|---|---|
| F1 | Regenerate the Notion token (shown on screen 26 Nov); clear it from `~/.zsh_history` | U |
| F2 | Separate Notion pages for Saffron Bridge and the book club | U |
| F3 | One PR `claude/finish-nov30` → `main`; close PR #3 as superseded. Merge only on the user's yes | C+U |
| F4 | Tag `v1.0-submission` after the merge; clean-clone install + test run | C |
| F5 | After the merge, restart the live app from the merged code (user pastes the key; same flow as 26 Nov) | C+U |

## Day by day
| Day | Claude | User |
|---|---|---|
| **Wed 26** (evening) | Branch, commit this plan; B3, B5; start B1 | F1; start A1 smoke run if possible |
| **Thu 27** | Finish B1, run B2 experiment; A2–A4 once the zip arrives; D1, D2, D4 | A1 full run (~3 h); answer E0 |
| **Fri 28** | C1, C2; D3, D5, D6; E1 draft | F2; read the draft |
| **Sat 29** | E1 revisions, E2 slides; rehearsal fixes | C3 rehearsal; C4 video |
| **Sun 30** | F3 PR (merge on yes), F4, F5, E3 exports | Approve merge; submit |

**Critical path:** A1 (user, ~3 h on Kaggle) → A2 → C2 → E1. If the zip isn't in by Thursday night, C2 and E1 go
ahead with v2 as final, and v3 becomes "trained after submission".

## Risks
- v3 fails its gate or Kaggle is unavailable: keep v2 and report v3 as negative. No demo impact.
- B2 regresses: keep it off and report the lexical limit.
- Live demo fails on the presentation Mac: backup video; the rehearsal is a day early on purpose.
- College format unknown: Markdown sources export to any format on the 30th.
