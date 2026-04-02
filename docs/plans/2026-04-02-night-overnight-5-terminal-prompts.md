# Overnight 5-Terminal Agent Prompts — 2026-04-02 Night

Generated: 2026-04-02 11:05 CDT
Machine: ace-linux-1 (dev-primary)
Repo root: /mnt/local-analysis/workspace-hub

## Strategic Focus

This batch executes **P0 market-driven package expansion** from #1676.
Job market scan (708 postings / 460 companies) identified three critical gaps:
- cathodic_protection: 131 jobs, only 15 modules + 4 test files
- ansys: 249 FEA jobs, only 14 modules + 3 test files
- fatigue: 92 jobs, only 8 modules + 5 test files

Terminals 1-3 do TDD expansion of these three packages in parallel.
Terminal 4 fixes test infrastructure and docstrings (carryover).
Terminal 5 hardens the solver queue pipeline.

## Provider Allocation

| Terminal | Provider      | Workstream                                    | Est. Time |
|----------|---------------|-----------------------------------------------|-----------|
| 1        | Claude        | cathodic_protection TDD expansion (3 modules) | 2-3 hrs   |
| 2        | Codex seat 1  | ansys TDD expansion (3 modules)               | 2-3 hrs   |
| 3        | Codex seat 2  | fatigue TDD expansion (3 modules)             | 2-3 hrs   |
| 4        | Gemini        | Test deps fix + error triage + docstrings     | 2-3 hrs   |
| 5        | Claude/Hermes | Solver queue hardening (retry+validator+cron) | 2-3 hrs   |

## Git Contention Avoidance Map

```
Terminal 1 writes: digitalmodel/src/digitalmodel/cathodic_protection/
                   digitalmodel/tests/cathodic_protection/

Terminal 2 writes: digitalmodel/src/digitalmodel/ansys/
                   digitalmodel/tests/ansys/

Terminal 3 writes: digitalmodel/src/digitalmodel/fatigue/
                   digitalmodel/tests/fatigue/

Terminal 4 writes: digitalmodel/pyproject.toml (deps only)
                   digitalmodel/src/digitalmodel/web/ (docstrings only)
                   digitalmodel/src/digitalmodel/reservoir/ (docstrings only)
                   digitalmodel/src/digitalmodel/infrastructure/ (docstrings only)
                   digitalmodel/src/digitalmodel/marine_ops/ (docstrings only)
                   docs/dashboards/

Terminal 5 writes: scripts/solver/
                   tests/solver/
                   config/cron/
                   docs/solver/

ZERO FILE OVERLAP confirmed.
T1/T2/T3 each own completely separate digitalmodel packages.
T4 only touches pyproject.toml deps + 4 separate docstring packages + dashboards.
T5 only touches solver scripts outside of digitalmodel entirely.
Each terminal does: git pull origin main --rebase before every push.
```

NOTE: Terminals 1-3 commit from inside `digitalmodel/` (nested git repo).
Terminals 4 commits from both `digitalmodel/` (pyproject.toml, docstrings) and
workspace-hub root (dashboards). Terminal 5 commits from workspace-hub root only.

## Issue-to-Terminal Reverse Mapping

| Issue | Title (abbreviated)                              | Terminal |
|------:|--------------------------------------------------|----------|
| #1676 | Market-Driven Repo Development — CP expansion    | T1       |
| #1676 | Market-Driven Repo Development — ANSYS expansion | T2       |
| #1676 | Market-Driven Repo Development — fatigue expansion| T3      |
| #1647 | Fix broken test deps (pint, plotly, deepdiff)    | T4       |
| #1665 | Triage 149 pytest collection errors              | T4       |
| #1645 | Docstring uplift wave 2 (4 packages)             | T4       |
| #1654 | Solver queue: retry logic + exponential backoff  | T5       |
| #1650 | Solver queue: batch manifest validation CLI      | T5       |
| #1648 | Solver queue: watch-results cron + JSONL dashboard| T5      |

## Prompt File Locations

- Terminal 1: docs/plans/overnight-prompts/2026-04-02-night/terminal-1-cathodic-protection-tdd.md
- Terminal 2: docs/plans/overnight-prompts/2026-04-02-night/terminal-2-ansys-expansion-tdd.md
- Terminal 3: docs/plans/overnight-prompts/2026-04-02-night/terminal-3-fatigue-expansion-tdd.md
- Terminal 4: docs/plans/overnight-prompts/2026-04-02-night/terminal-4-test-infra-docstrings.md
- Terminal 5: docs/plans/overnight-prompts/2026-04-02-night/terminal-5-solver-hardening.md

## What You'll Have By Morning

From Terminal 1 (Claude — cathodic_protection):
  ✓ anode_sizing.py — sacrificial anode design per DNV-RP-B401
  ✓ pipeline_cp.py — pipeline CP design per API RP 1169 / ISO 15589-1
  ✓ marine_cp.py — offshore structure multi-zone CP assessment
  ✓ 20+ new test cases across 3 new test files

From Terminal 2 (Codex 1 — ansys):
  ✓ Extended pressure_vessel.py — ASME VIII Div 1 calcs
  ✓ Extended batch_runner.py — multi-load-case management
  ✓ results_extractor.py — stress/displacement/reaction extraction
  ✓ 22+ new test cases across 3 new test files

From Terminal 3 (Codex 2 — fatigue):
  ✓ sn_library_api.py — programmatic API for 221 S-N curves
  ✓ hotspot_stress.py — DNV-RP-C203 Type A/B hotspot methodology
  ✓ scf_library.py — Efthymiou tubular joint SCF equations
  ✓ 26+ new test cases across 3 new test files

From Terminal 4 (Gemini — test infra + docs):
  ✓ Fixed test deps in pyproject.toml (pint, plotly, deepdiff, etc.)
  ✓ Test error triage report in docs/dashboards/
  ✓ Docstring uplift for web, reservoir, infrastructure, marine_ops

From Terminal 5 (Claude/Hermes — solver):
  ✓ retry_handler.py — exponential backoff for failed solver jobs
  ✓ validate_manifest.py — CLI for batch manifest schema enforcement
  ✓ results_dashboard.py — JSONL dashboard + cron integration
  ✓ 22+ new test cases across 3 new test files

Issues addressed: #1676 (P0), #1647, #1665, #1645, #1654, #1650, #1648
New modules: 9 new source files, 9 new test files
New test cases: ~90 total across all terminals
Package expansion: CP 15→18, ANSYS 14→14+ (extended), fatigue 8→11
