# Overnight 5-Terminal Agent Prompts — 2026-04-03

Generated: 2026-04-03 06:45 CDT
Machine: ace-linux-1 (dev-primary)
Repo root: /mnt/local-analysis/workspace-hub

## Provider Allocation

| Terminal | Provider      | Workstream                                     | Est. Time |
|----------|---------------|------------------------------------------------|-----------|
| 1        | Claude        | OrcaWave/Marine Pipeline TDD (3 high-pri)      | 2-3 hrs   |
| 2        | Codex seat 1  | Hull/OrcaFlex Test Suite (4 test packages)     | 2-3 hrs   |
| 3        | Codex seat 2  | Test Deps Fix + SKELETON Package Uplift        | 2-3 hrs   |
| 4        | Gemini        | Document Intelligence Pipeline (4 tasks)       | 2-3 hrs   |
| 5        | Claude/Hermes | Docstring Uplift + Cron Automation             | 2-3 hrs   |

## Git Contention Avoidance Map

```
Terminal 1 writes: digitalmodel/src/digitalmodel/orcawave/,
                   digitalmodel/src/digitalmodel/specs/,
                   digitalmodel/tests/orcawave/,
                   digitalmodel/tests/specs/

Terminal 2 writes: digitalmodel/tests/parametric_hull/,
                   digitalmodel/tests/orcaflex/,
                   digitalmodel/tests/hydrodynamics/ (new damping tests only)

Terminal 3 writes: digitalmodel/pyproject.toml (deps only),
                   digitalmodel/tests/web/,
                   digitalmodel/tests/field_development/,
                   digitalmodel/tests/geotechnical/,
                   digitalmodel/tests/nde/,
                   digitalmodel/tests/reservoir/,
                   digitalmodel/src/digitalmodel/reservoir/stratigraphic.py

Terminal 4 writes: scripts/document-intelligence/ (new files only),
                   tests/document-intelligence/,
                   docs/document-intelligence/,
                   data/document-index/ (new index files only)

Terminal 5 writes: digitalmodel/src/digitalmodel/{web,reservoir,infrastructure,
                   marine_ops,solvers,hydrodynamics,specialized,signal_processing}/
                   (docstrings only — no logic changes),
                   config/cron/, scripts/cron/

ZERO FILE OVERLAP confirmed.
T5 writes docstrings to reservoir/ but NOT stratigraphic.py (T3 owns that).
T2 writes new damping tests to hydrodynamics/ tests; T5 writes docstrings to source — no overlap.
Each terminal does: git pull origin main before every push.
```

## Issue-to-Terminal Reverse Mapping

| Issue | Title (abbreviated)                              | Terminal |
|------:|--------------------------------------------------|----------|
| #1588 | Parametric spec.yml generator                    | T1       |
| #1597 | RAO extractor pipeline                           | T1       |
| #1638 | DiffractionSpec reverse parser                   | T1       |
| #1599 | Parametric hull analysis tests (forward_speed)   | T2       |
| #1601 | Parametric hull analysis tests (all 4 modules)   | T2       |
| #1605 | OrcaWave-to-OrcaFlex integration test            | T2       |
| #1606 | OrcaWave damping-sweep test suite                | T2       |
| #1647 | Fix broken test deps (pint, plotly, deepdiff)    | T3       |
| #1584 | Test coverage: web package (69 files, 0 tests)   | T3       |
| #1589 | Test coverage: SKELETON packages (4 packages)    | T3       |
| #1633 | Refactor reservoir/stratigraphic.py              | T3       |
| #1641 | Conference indexing Phase 1 (1,032 files)         | T4       |
| #1612 | ASTM standards-ledger expansion                  | T4       |
| #1640 | Install tesseract-ocr + validate OCR             | T4       |
| #1643 | Register OCR parser in registry                  | T4       |
| #1645 | Docstring uplift wave 2 (4 packages)             | T5       |
| #1646 | Docstring uplift wave 3 (4 packages)             | T5       |
| #1590 | Automate architecture scanner as cron            | T5       |
| #1625 | Schedule staleness scanner as cron               | T5       |

## Prompt File Locations

- Terminal 1: docs/plans/overnight-prompts/2026-04-03/terminal-1-orcawave-marine-tdd.md
- Terminal 2: docs/plans/overnight-prompts/2026-04-03/terminal-2-hull-orcaflex-tests.md
- Terminal 3: docs/plans/overnight-prompts/2026-04-03/terminal-3-test-deps-skeleton-uplift.md
- Terminal 4: docs/plans/overnight-prompts/2026-04-03/terminal-4-document-intelligence.md
- Terminal 5: docs/plans/overnight-prompts/2026-04-03/terminal-5-docstring-cron-automation.md

## What You'll Have By Morning

```
From Terminal 1 (Claude — OrcaWave/Marine TDD):
  ✓ Parametric spec.yml generator — hull params to DiffractionSpec YAML
  ✓ RAO extractor pipeline — .owr files to RAODatabase
  ✓ DiffractionSpec reverse parser — native YAML back to spec
  ✓ 12+ new tests across 3 test files in orcawave/

From Terminal 2 (Codex 1 — Hull/OrcaFlex Tests):
  ✓ test_forward_speed.py + test_shallow_water.py — parametric hull tests
  ✓ test_passing_ship.py + test_charts.py — interaction + visualization tests
  ✓ test_orcawave_integration.py — OrcaWave→OrcaFlex RAO handoff validation
  ✓ test_damping_sweep.py — viscous roll damping parametric suite
  ✓ 20+ new tests across 6 test files

From Terminal 3 (Codex 2 — Test Deps + SKELETON Uplift):
  ✓ pint, plotly, deepdiff added to dev dependencies (unblocks test suites)
  ✓ web package: import + core unit tests (69 files covered)
  ✓ field_development, geotechnical, nde: import + unit tests each
  ✓ reservoir/stratigraphic.py refactored from raw script to module
  ✓ 4 SKELETON packages → DEVELOPMENT maturity

From Terminal 4 (Gemini — Document Intelligence):
  ✓ Conference indexer Python tool + Phase 1 index (1,032 files)
  ✓ ASTM standards-ledger scanner + domain classification
  ✓ tesseract-ocr installed and validated on real scans
  ✓ OCR parser registered in doc-intelligence pipeline

From Terminal 5 (Claude/Hermes — Docstring + Cron):
  ✓ 8 packages get docstring uplift (wave 2 + wave 3)
  ✓ Architecture scanner scheduled as weekly cron (Sunday 2 AM)
  ✓ Staleness scanner scheduled as weekly cron (Sunday 3 AM)
  ✓ Two new cron wrapper scripts in scripts/cron/

Issues addressed: #1584, #1588, #1589, #1590, #1597, #1599, #1601, #1605,
                  #1606, #1612, #1625, #1633, #1638, #1640, #1641, #1643,
                  #1645, #1646, #1647
Total: 19 issues across 5 terminals
New tools: 5+ reusable scripts/modules
New tests: 40+ test functions across ~15 test files
```
