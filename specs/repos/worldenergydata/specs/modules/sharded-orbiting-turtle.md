---
title: "Flatten worldenergydata Module Structure"
work_item: WRK-096
version: 1.0
module: worldenergydata
session:
  id: 2026-02-08-wrk096-plan
  agent: claude-opus-4.6
review:
  cross_review: pending-implementation
  plan_review: completed (2026-02-04, 3 iterations)
---

# WRK-096: Flatten worldenergydata Module Structure

## Context

The worldenergydata package nests all 17 domain modules under `src/worldenergydata/modules/`, requiring verbose imports like `from worldenergydata.modules.bsee import bsee`. This mirrors the problem solved by WRK-066 in digitalmodel, but worldenergydata is simpler (17 modules vs 75+). The goal is to flatten modules to `worldenergydata.X` for discoverability while maintaining backward compatibility.

**Scope**: 725 internal imports across 226 files. Zero external Python consumers. One CLI entry point.

**Decision: Flatten only (no domain grouping)** - 17 modules with semantic names don't need an extra grouping layer.

---

## Pre-Step: Commit Plan & Link

worldenergydata is a git submodule. Commits must happen inside the submodule first:
1. Inside worldenergydata: `git add specs/modules/sharded-orbiting-turtle.md && git commit`
2. Inside workspace-hub: `git add .claude/work-queue/working/WRK-096.md worldenergydata && git commit`

## Phase 0: Safety Net

**Branch**: `refactor/wrk-096-module-structure`

1. Create git tag `pre-wrk-096`
2. Create feature branch
3. Resolve CLAUDE.md merge conflict (keep HEAD/workspace-hub style)
4. Run baseline tests: `uv run pytest tests/ -v --tb=short`; record pass/fail counts
5. Generate import map: scan all `from worldenergydata.modules.` references

**Files**:
- `CLAUDE.md` - resolve merge conflict
- `scripts/refactor/generate-import-map.py` - new, ~50 lines

**Gate**: Tag exists, baseline recorded, branch created.

---

## Phase 1: Backward Compatibility Layer

Create MetaPathFinder that redirects `worldenergydata.modules.X` to `worldenergydata.X` with DeprecationWarning. Pattern copied from `digitalmodel/src/digitalmodel/_compat.py`.

1. Create `src/worldenergydata/_compat.py` (~150 lines)
   - `_MOVED_MODULES` set with all 17 module names
   - `_ModulesRedirectFinder(MetaPathFinder)` + `_RedirectLoader`
   - `install_redirect()` function to register on `sys.meta_path`
2. Create `src/worldenergydata/modules/__init__.py` (~30 lines)
   - `__getattr__` for attribute-level redirects
3. Update `src/worldenergydata/__init__.py`
   - Import and activate compat layer
   - Add comprehensive module catalog docstring
   - Sync `__version__` to `"0.1.0"` (match pyproject.toml)

**Reference**: `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/_compat.py`

**Gate**: Old imports work (with DeprecationWarning), tests pass.

---

## Phase 2: Flatten Modules (3 batches)

Physically `git mv` each module from `modules/X` to top-level `X`.

### Batch 1 (6 modules): bsee, canada, fdas, hse, landman, lng_terminals
### Batch 2 (6 modules): marine_safety, metocean, mexico_cnh, pipeline_safety, reporting, safety_analysis
### Batch 3 (5 modules): sodir, texas_rrc, vessel_hull_models, well_production_dashboard + `analysis/lower_tertiary` → `lower_tertiary`

After each batch:
- `uv run pytest tests/modules/<moved> -v --tb=short`
- Test CLI: `uv run worldenergydata <module> --help`
- Test direct import: `uv run python -c "from worldenergydata.<module> import ..."`

**Gate**: All 17+1 modules moved, CLI functional, batch tests pass.

---

## Phase 3: Update Internal Imports

725 `from worldenergydata.modules.X` references across 226 files.

1. Create `scripts/refactor/update-imports.py` (~80 lines)
   - Regex: `from worldenergydata\.modules\.(\w+)` → `from worldenergydata.\1`
   - Scan `src/worldenergydata/` and `tests/`
   - Report: files changed, imports updated
2. Run on src/ and tests/
3. Manually verify CLI commands (`src/worldenergydata/cli/commands/*.py` - 11 files)
4. Verify zero stale references remain (except `_compat.py` and `modules/__init__.py`)

**Key files to update**:
- `src/worldenergydata/engine.py` (7 refs)
- `src/worldenergydata/cli/commands/*.py` (11 files, ~40 refs total)
- `src/worldenergydata/cli/main.py` (1 ref)
- All intra-module imports (bulk of 725)

**Gate**: `grep -r "worldenergydata\.modules\." src/ --include="*.py" | grep -v _compat | grep -v modules/__init__` returns empty.

---

## Phase 4: Clean Up src/ Level

1. Delete empty placeholders: `src/external/`, `src/modules/`
2. Absorb `src/validators/data_validator.py` into `src/worldenergydata/common/validation/`
3. Rename `src/worldenergydata/base_configs/modules/` → `base_configs/templates/` (avoid confusion)
4. Update `pyproject.toml` package discovery:
   ```toml
   include = ["worldenergydata*"]  # remove "external*", "modules*", "validators*"
   ```
5. Delete empty `src/worldenergydata/analysis/` directory (after lower_tertiary moved out)

**Files**:
- `pyproject.toml` (line ~126-129)
- `src/validators/` → absorbed
- `src/external/` → deleted
- `src/modules/` → deleted

**Gate**: `ls src/` shows only `worldenergydata/`, tests pass.

---

## Phase 5: Documentation

1. Update `src/worldenergydata/__init__.py` with full module catalog docstring (grouped by domain for readability, not for import paths)
2. Add README.md to 14 modules missing them (template: overview, usage, CLI, structure)
3. Create `docs/MODULE_INDEX.md` - table of all modules with description, file count, CLI status
4. Update root `README.md` import examples

**Gate**: All 17 modules have README.md, __init__ docstring complete.

---

## Phase 6: Validation

1. Full test suite: `uv run pytest tests/ -v --tb=short` - compare to Phase 0 baseline
2. CLI validation: all 11 commands respond to `--help`
3. Entry point: `uv run worldenergydata --help` and `--version`
4. Import validation script: test all 17 new paths + 17 old paths (with warning)
5. Legal scan: `./scripts/legal/legal-sanity-scan.sh --repo=worldenergydata`

**Gate**: Tests match baseline, CLI works, legal scan passes.

---

## Phase 7: Commit & Archive WRK-096

1. Commit with conventional message: `feat(structure): flatten modules/ for discoverability (WRK-096)`
2. Create `docs/MIGRATION_GUIDE.md` documenting old→new import paths
3. Archive WRK-096 in work queue

**Deprecation timeline**:
- v0.1.0: Old imports work with DeprecationWarning
- v0.2.0: Warnings escalated
- v0.3.0: `modules/__init__.py` and `_compat.py` removed

---

## Rollback

- Pre-refactor tag: `pre-wrk-096`
- Feature branch isolates all changes
- Compat layer ensures old imports never break during transition
- `git checkout pre-wrk-096` restores original state

## Files Summary

| File | Action |
|------|--------|
| `src/worldenergydata/_compat.py` | Create (~150 lines) |
| `src/worldenergydata/modules/__init__.py` | Create (~30 lines) |
| `src/worldenergydata/__init__.py` | Update (docstring + compat activation) |
| `src/worldenergydata/modules/*` | git mv to `src/worldenergydata/*` |
| `src/worldenergydata/cli/commands/*.py` | Update imports (11 files) |
| `src/worldenergydata/engine.py` | Update imports |
| `pyproject.toml` | Update package discovery |
| `CLAUDE.md` | Resolve merge conflict |
| `scripts/refactor/update-imports.py` | Create (~80 lines) |
| `scripts/refactor/generate-import-map.py` | Create (~50 lines) |
| `docs/MODULE_INDEX.md` | Create |
| `docs/MIGRATION_GUIDE.md` | Create |
| 14 module README.md files | Create |
| `src/external/`, `src/modules/`, `src/validators/` | Delete/absorb |
