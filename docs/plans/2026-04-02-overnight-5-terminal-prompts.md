# Overnight 5-Terminal Agent Prompts — 2026-04-02

Generated: 2026-04-02 06:30 CDT
Machine: ace-linux-1 (dev-primary)
Repo root: /mnt/local-analysis/workspace-hub

## Provider Allocation

| Terminal | Provider      | Workstream                                    | Est. Time |
|----------|---------------|-----------------------------------------------|-----------| 
| 1        | Claude        | Solver Queue Hardening + OrcaFlex Tests       | 2-3 hrs   |
| 2        | Codex seat 1  | Docstring Uplift (7 packages → PRODUCTION)    | 2-3 hrs   |
| 3        | Codex seat 2  | Architecture Scanner Enhancements + Maturity  | 2-3 hrs   |
| 4        | Gemini        | Test Health Dashboard + Reservoir Refactor    | 2-3 hrs   |
| 5        | Claude/Hermes | Document Intelligence: Marine + Cross-Ref     | 2-3 hrs   |

## Git Contention Avoidance Map

```
Terminal 1 writes: scripts/solver/, digitalmodel/tests/orcaflex/,
                   digitalmodel/tests/solver/, data/solver-manifests/
Terminal 2 writes: digitalmodel/src/digitalmodel/{structural,subsea,asset_integrity,
                   naval_architecture,production_engineering,well,ansys}/ (docstrings only)
Terminal 3 writes: scripts/analysis/, tests/analysis/, docs/architecture/,
                   digitalmodel/src/digitalmodel/data_models/__init__.py
Terminal 4 writes: scripts/quality/, tests/quality/, docs/dashboards/,
                   digitalmodel/src/digitalmodel/reservoir/stratigraphic.py,
                   digitalmodel/tests/reservoir/, config/cron/
Terminal 5 writes: scripts/document-intelligence/, tests/document-intelligence/,
                   docs/document-intelligence/, data/document-index/

ZERO OVERLAP confirmed.
Each terminal does: git pull origin main before each push.
```

## Prompt File Locations

- Terminal 1: docs/plans/overnight-prompts/2026-04-02/terminal-1-solver-queue-hardening.md
- Terminal 2: docs/plans/overnight-prompts/2026-04-02/terminal-2-docstring-promotion.md
- Terminal 3: docs/plans/overnight-prompts/2026-04-02/terminal-3-arch-scanner-enhancements.md
- Terminal 4: docs/plans/overnight-prompts/2026-04-02/terminal-4-test-health-dashboard.md
- Terminal 5: docs/plans/overnight-prompts/2026-04-02/terminal-5-doc-intelligence-marine.md

## What You'll Have By Morning

```
From Terminal 1 (Claude — Solver Queue Hardening):
  ✓ scripts/solver/submit-batch.sh — batch job submission from YAML manifest
  ✓ scripts/solver/watch-results.sh — automatic result watching + post-processing
  ✓ scripts/solver/queue-health.sh — queue health monitoring report
  ✓ digitalmodel/tests/orcaflex/ — 6+ test files (1 → 6+, targeting PRODUCTION)
  ✓ tests/solver/ — batch submission + result watcher tests

From Terminal 2 (Codex — Docstring Promotion):
  ✓ ~80 files across 7 packages get module-level docstrings
  ✓ structural: 37% → 55%+ docstring coverage
  ✓ subsea: 28% → 55%+ docstring coverage
  ✓ asset_integrity: 21% → 55%+
  ✓ naval_architecture: 5% → 55%+
  ✓ production_engineering, well, ansys: 0% → 55%+

From Terminal 3 (Codex — Architecture Enhancements):
  ✓ data_models/__init__.py — package now visible (30 → 31 packages)
  ✓ API name collision detection across 3,271+ symbols
  ✓ LOC-weighted scoring + trend tracking in module status matrix
  ✓ Updated maturity tracker: 5 packages SKELETON → DEVELOPMENT

From Terminal 4 (Gemini — Quality + Reservoir):
  ✓ docs/dashboards/test-health-dashboard.md — per-package test pass/fail report
  ✓ scripts/quality/test-health-dashboard.py — reusable dashboard generator
  ✓ reservoir/stratigraphic.py — refactored to importable module with tests
  ✓ config/cron/ — architecture + staleness scanners scheduled weekly

From Terminal 5 (Claude/Hermes — Document Intelligence):
  ✓ scripts/document-intelligence/batch-process-standards.py — marine standards batch processor
  ✓ scripts/document-intelligence/marine-taxonomy-classifier.py — 7+ sub-domain taxonomy
  ✓ scripts/document-intelligence/cross-reference-registries.py — online ↔ local cross-ref
  ✓ docs/document-intelligence/ — marine taxonomy report + cross-reference report

Issues addressed: #1573, #1586, #1587, #1590, #1595, #1602, #1608, #1613,
                  #1621, #1622, #1625, #1626, #1627, #1628, #1629, #1633, #1634
Total: 17 issues progressed
New tools: 7 reusable scripts
Package promotions: 7 packages gain >50% docstrings, 2+ gain PRODUCTION test threshold
```

## Issue-to-Terminal Mapping

| Issue | Title (abbreviated)                              | Terminal |
|------:|--------------------------------------------------|----------|
| #1586 | Solver queue hardening                           | T1       |
| #1595 | Solver batch submission + result watcher          | T1       |
| #1628 | Sprint plan Phase 1                              | T1       |
| #1602 | DEVELOPMENT → PRODUCTION promotion (orcaflex)     | T1       |
| #1587 | Docstring uplift (structural, subsea, 5 more)     | T2       |
| #1602 | DEVELOPMENT → PRODUCTION promotion (docstrings)   | T2       |
| #1626 | data_models missing __init__.py                   | T3       |
| #1627 | API name collision detection                      | T3       |
| #1629 | LOC-weighted scoring for status matrix            | T3       |
| #1634 | Update maturity tracker (5 SKELETON → DEV)        | T3       |
| #1573 | Cross-repo test health dashboard                  | T4       |
| #1633 | Refactor reservoir/stratigraphic.py               | T4       |
| #1590 | Automate scanners as cron tasks                   | T4       |
| #1625 | Schedule staleness scanner                        | T4       |
| #1621 | Marine standards batch processor                  | T5       |
| #1622 | Marine sub-domain taxonomy                        | T5       |
| #1613 | Cross-reference registries                        | T5       |
