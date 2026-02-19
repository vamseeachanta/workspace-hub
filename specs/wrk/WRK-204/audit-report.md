# WRK-204 Audit Report — digitalmodel modules/ rename impact

Generated: 2026-02-19 by Explore agent (aa47e1c)

## Executive Summary

| Metric | Value |
|--------|-------|
| Total files to rename | 9,736 |
| Total references to update | 792 |
| Complexity | Medium (large scope, mostly docs; 1 critical runtime config update) |
| Estimated effort | 4–5 hours execution + testing |

## Directory Breakdown

| Path | Files | References | Python Import Risk | Difficulty |
|------|-------|------------|-------------------|------------|
| `docs/modules/` | 9,325 | 459 (173py/271md/15cfg) | NONE (static docs) | EASY |
| `examples/modules/` | 99 | 86 (86md) | NONE | EASY |
| `scripts/python/digitalmodel/modules/` | 232 | 0 | NONE | VERY EASY |
| `src/digitalmodel/infrastructure/base_configs/modules/` | 78 | 17 (7py/10md) | MEDIUM (config loader) | MEDIUM |
| `tests/modules/` | 2 | 276 (30py/196md/3sh) | MEDIUM (test imports) | MEDIUM |
| **TOTAL** | **9,736** | **792** | | **PHASED** |

## Critical Findings

### 1. No `src/digitalmodel/modules/` directory
`src/digitalmodel/` uses domain-group structure (hydrodynamics, solvers, etc.) — skip entirely.

### 2. `digitalmodel.modules.*` Python imports (28 files)
Pattern: `from digitalmodel.modules.signal_analysis.orcaflex import ...`
All in `scripts/python/digitalmodel/tools/` — migration/legacy tools only.
**Decision: keep as-is, do NOT rename.**

### 3. Runtime config paths — CRITICAL
`src/digitalmodel/infrastructure/base_configs/modules/` is loaded by config framework.
Files affected: `config_framework.py`, `config_models.py`, 5 other config loaders.
**Breaking change if renamed without updating framework.**

### 4. Test infrastructure
`tests/modules/` has 2 test files + 30 cleanup tool references.

## Recommended Phases

### Phase 1 — Zero-risk (30 min)
- `examples/modules/` → `examples/domains/` (86 md-only refs, self-contained)
- `scripts/python/digitalmodel/modules/` → `scripts/python/digitalmodel/analysis/` (no external refs)

### Phase 2 — Docs bulk rename (2 hours, scripted)
- `docs/modules/` → `docs/domains/` (9,325 files)
- Update 271 markdown refs with `git grep | sed`
- Update 3 skill files + FOLDER_CONVENTIONS.md

### Phase 3 — Runtime config (CRITICAL, 1–2 hours + review)
- `src/digitalmodel/infrastructure/base_configs/modules/` → `.../domains/`
- Update `config_framework.py` path references (7 lines)
- Update `config_models.py`
- Run full config loader tests
- **Requires code review gate before merge**

### Phase 4 — Test infrastructure (2 hours)
- `tests/modules/` → `tests/domains/`
- Update 30 cleanup tool refs, 196 md refs, 3 shell scripts
- Run pytest discovery + `tests/domains/`

## Reference Update Totals

| Type | Count | Approach |
|------|-------|----------|
| Markdown (.md) | 564 | Bulk grep-sed, 45 min |
| Python (.py) | 210 | Cleanup/tool scripts, 1 hour |
| YAML/JSON | 15 | Config files, manual review |
| Shell (.sh) | 3 | Manual, 30 min |

## Post-Rename Validation

```bash
git grep "docs/modules"             # should return 0
git grep "examples/modules"         # should return 0
git grep "tests/modules"            # should return 0
git grep "base_configs/modules"     # should return 0
PYTHONPATH=src python3 -m pytest tests/domains/ --noconftest
```

## Risk Mitigation

1. Phase-based — complete 1–2 (safe) before 3–4
2. `git mv` to preserve history (not cp + rm)
3. Tag before each phase for easy rollback
4. Phase 3 requires explicit plan approval before execution

## Files Needing Code Updates (non-markdown)

**Production (Phase 3):**
- `src/digitalmodel/infrastructure/base_configs/config_framework.py`
- `src/digitalmodel/infrastructure/base_configs/config_models.py`
- 5 other config loader files

**Tools/scripts (Phase 4):**
- `scripts/bash/digitalmodel/tools/run-test-py_orcaflex.sh`
- `scripts/bash/digitalmodel/tools/run-test-py.sh`
- `scripts/bash/digitalmodel/tools/run-test-yml.sh`
- 30 files in `scripts/python/digitalmodel/tools/`
