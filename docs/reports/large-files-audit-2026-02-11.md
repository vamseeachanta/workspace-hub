# Large Files Audit — 2026-02-11

> Coding style rule: 400-line hard limit, 200-line soft target (`coding-style.md`)

## Summary

| Scope | Files >400 lines |
|-------|-----------------|
| workspace-hub `scripts/` + `.claude/` | 28 |
| worldenergydata `src/` | 204 |
| worldenergydata `scripts/` + `tests/` | 157 |
| digitalmodel `src/` | 304 |
| **Total** | **693** |

## Workspace-Hub (28 files — directly owned)

### Top offenders

| Lines | File | Category |
|-------|------|----------|
| 1052 | `scripts/development/testing/unified_test_runner.py` | Test infra |
| 961 | `scripts/operations/system/system-update.sh` | Ops script |
| 792 | `.claude/skills/.../daily-reflect.sh` | Reflect skill |
| 789 | `scripts/development/ai-review/codex-review-manager.sh` | AI review |
| 743 | `.claude/skills/.../create-skills.sh` | Skill gen |
| 716 | `.claude/skills/.../eval-skills.py` | Skill eval |
| 695 | `scripts/data/og-standards/catalog.py` | Data catalog |
| 649 | `scripts/ai/assessment/assess-ai-tools.sh` | AI assessment |
| 605 | `scripts/data/python/translate_excel.py` | Data util |

### Categorization

- **Split candidates** (multiple responsibilities): `unified_test_runner.py`, `system-update.sh`, `codex-review-manager.sh`
- **Acceptable as-is** (single-purpose scripts): `daily-reflect.sh`, `assess-ai-tools.sh`, `translate_excel.py`
- **Should be refactored eventually**: `catalog.py`, `generate-index.py`, `dedup.py`, `search.py`

## worldenergydata `src/` Top 10

| Lines | File | Notes |
|-------|------|-------|
| 1653 | `common/legacy/ong_fd_components.py` | Legacy, already has `_refactored` sibling |
| 1550 | `safety_analysis/taxonomy/activity_taxonomy.py` | Taxonomy data — acceptable |
| 1537 | `lng_terminals/collectors/seed_collector.py` | Split: scraping + parsing + storage |
| 1251 | `common/legacy/wellpath3D.py` | Legacy — low ROI to refactor |
| 1131 | `well_production_dashboard/field_aggregation.py` | Split: aggregation + formatting |
| 1090 | `well_production_dashboard/well_production.py` | Split candidate |
| 1077 | `bsee/analysis/well_data_verification/quality.py` | Split: rules + execution |
| 1053 | `cli/commands/landman.py` | CLI — many subcommands |
| 1040 | `marine_safety/reports/quality_dashboard.py` | Split: data + rendering |
| 1032 | `sodir/cross_regional.py` | Split candidate |

## digitalmodel `src/` Top 10

| Lines | File | Notes |
|-------|------|-------|
| 1985 | `infrastructure/common/wellpath3D.py` | Duplicate of worldenergydata |
| 1905 | `solvers/orcaflex/orcaflex_model_components.py` | Core solver — careful split |
| 1660 | `solvers/orcaflex/pipeline_schematic.py` | Visualization — split |
| 1586 | `hydrodynamics/diffraction/benchmark_plotter.py` | Plotting — split |
| 1531 | `infrastructure/common/cathodic_protection.py` | Engineering calcs |
| 1476 | `structural/pipe_capacity/custom/PipeCapacity.py` | Engineering calcs |
| 1439 | `marine_ops/.../integration_charts.py` | Visualization — split |
| 1290 | `subsea/catenary_riser/legacy/orcaflexModel.py` | Legacy |
| 1275 | `marine_ops/.../validate_phase2.py` | Validation — split |
| 1255 | `data_systems/.../BS7910_critical_flaw_limits.py` | Code reference data |

## Exclusion List

Files that should NOT be flagged in future audits:

### Auto-generated / data-definition files
- `*/taxonomy/*.py` — taxonomy data definitions
- `*/legacy/*.py` — frozen legacy code (refactor = high risk, low ROI)
- `*/BS7910_*.py`, `*/API579_*.py` — engineering code standard implementations
- `*/PipeCapacity.py` — pipe capacity calculation reference

### Test fixtures and archived tests
- `tests/_archived_tests/**` — already excluded from test runs
- `tests/**/fixtures/**` — test data

### Scripts that are single-purpose utilities
- `scripts/operations/system/*.sh` — system ops (run infrequently)
- `scripts/ai/assessment/*.sh` — assessment tools

## Recommended Refactoring Priority

**Tier 1 — High edit frequency, clear split boundaries:**
1. `unified_test_runner.py` (1052 lines) — split into runner, reporter, config
2. `codex-review-manager.sh` (789 lines) — split into review, formatting, submission
3. `lng_terminals/collectors/seed_collector.py` (1537 lines) — split: scrape, parse, store
4. `well_production_dashboard/field_aggregation.py` (1131 lines) — split: aggregate, format

**Tier 2 — Medium priority:**
5. `marine_safety/reports/quality_dashboard.py` (1040 lines)
6. `sodir/cross_regional.py` (1032 lines)
7. `bsee/analysis/well_data_verification/quality.py` (1077 lines)

**Tier 3 — Low priority (legacy/stable):**
8-10. Legacy files, engineering code standards, frozen reference implementations

## Next Steps

- [ ] Add `.large-files-exclusions.yaml` to workspace-hub for automated scanning
- [ ] Create WRK items for Tier 1 refactoring candidates
- [ ] Add `make lint-size` target to flag new violations
