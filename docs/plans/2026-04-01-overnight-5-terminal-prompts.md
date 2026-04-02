# Overnight 5-Terminal Agent Prompts — 2026-04-01

Generated: 2026-04-01 23:44 CDT
Machine: ace-linux-1 (dev-primary)
Repo root: /mnt/local-analysis/workspace-hub

## Provider Allocation

| Terminal | Provider      | Workstream                              | Est. Time |
|----------|---------------|-----------------------------------------|-----------|
| 1        | Claude        | Architecture Intelligence + Roadmaps   | 2-3 hrs   |
| 2        | Codex seat 1  | OrcaWave Test Coverage + Pipeline TDD   | 2-3 hrs   |
| 3        | Codex seat 2  | Test Coverage Uplift (SKELETON pkgs)    | 2-3 hrs   |
| 4        | Gemini        | Doc Staleness Scanner + Doc Refresh     | 2-3 hrs   |
| 5        | Claude/Hermes | Document Intelligence Pipeline Hardening| 2-3 hrs   |

## Git Contention Avoidance Map

```
Terminal 1 writes: docs/architecture/, docs/roadmaps/
Terminal 2 writes: digitalmodel/tests/orcawave/, digitalmodel/tests/solver/
Terminal 3 writes: digitalmodel/tests/field_development/, tests/geotechnical/, tests/nde/, tests/reservoir/, tests/web/
Terminal 4 writes: scripts/docs/, docs/dashboards/, docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md, docs/SKILLS_INDEX.md, docs/modules/tiers/TIER2_REPOSITORY_INDEX.md
Terminal 5 writes: scripts/document-intelligence/, docs/document-intelligence/

ZERO OVERLAP confirmed.
Each terminal does: git pull origin main before each push.
```

## What You'll Have By Morning

```
From Terminal 1 (Claude — Architecture Intelligence):
  ✓ docs/architecture/api-surface-map.md — API surface + import dependency graph for digitalmodel
  ✓ docs/architecture/module-status-matrix.md — consolidated cross-repo module status
  ✓ docs/roadmaps/orcawave-orcaflex-capability-roadmap.md — domain capability roadmap
  ✓ GH comment on #1567, #1604, #1572

From Terminal 2 (Codex — OrcaWave TDD):
  ✓ digitalmodel/tests/orcawave/ — test suite for 13 orcawave source files
  ✓ digitalmodel/tests/solver/test_spec_generator.py — parametric spec.yml generation tests
  ✓ GH comment on #1585, #1596, #1598

From Terminal 3 (Codex — SKELETON Package Uplift):
  ✓ Tests for field_development, geotechnical, nde, reservoir packages
  ✓ Tests for web package (priority subset — 10+ test files)
  ✓ GH comment on #1589, #1584

From Terminal 4 (Gemini — Doc Refresh + Staleness Scanner):
  ✓ scripts/docs/staleness-scanner.py — automated staleness detection tool
  ✓ docs/dashboards/doc-freshness-dashboard.md — current staleness report
  ✓ Updated docs/WORKSPACE_HUB_CAPABILITIES_SUMMARY.md
  ✓ Updated docs/SKILLS_INDEX.md
  ✓ Updated docs/modules/tiers/TIER2_REPOSITORY_INDEX.md
  ✓ GH comment on #1568, #1571

From Terminal 5 (Claude/Hermes — Doc Intelligence Pipeline):
  ✓ scripts/document-intelligence/ocr-parser.py — OCR extraction for scanned PDFs
  ✓ scripts/document-intelligence/xlsx-formula-extractor.py — raised size limit
  ✓ docs/document-intelligence/conference-index-plan.md — index plan for 38K conference files
  ✓ GH comment on #1617, #1619, #1608

Issues addressed: #1567, #1568, #1571, #1572, #1584, #1585, #1589, #1596, #1598, #1604, #1608, #1617, #1619
New tools: 3 reusable scripts (staleness scanner, OCR parser, XLSX extractor)
```

---

## PROMPT 1 — Terminal 1 (Claude) — Architecture Intelligence + Roadmaps

Issues: #1604, #1567, #1572

---

## PROMPT 2 — Terminal 2 (Codex seat 1) — OrcaWave Test Coverage + Pipeline TDD

Issues: #1585, #1596, #1598

---

## PROMPT 3 — Terminal 3 (Codex seat 2) — SKELETON Package Test Uplift

Issues: #1589, #1584

---

## PROMPT 4 — Terminal 4 (Gemini) — Doc Staleness Scanner + Doc Refresh

Issues: #1568, #1571

---

## PROMPT 5 — Terminal 5 (Claude/Hermes) — Document Intelligence Pipeline

Issues: #1617, #1619, #1608
