# Tier-1 Repos Deep Refactor — Design Spec

**Date:** 2026-04-09
**Repos:** digitalmodel, assetutilities, worldenergydata
**Approach:** Hybrid — Foundation First + Parallel Consumers

---

## Context

Three tier-1 repos need modernization across packaging, architecture, code quality, testing, and data management. They share a strict dependency hierarchy:

```
assetutilities  (39K SLOC — foundation library)
    ↑ editable path dep       ↑ git+https dep
    │                         │
digitalmodel              worldenergydata
(438K SLOC)               (265K SLOC)
```

assetutilities is the only shared dependency. digitalmodel and worldenergydata do not depend on each other.

## Approach: Hybrid

1. Stabilize assetutilities first (sequential — it blocks both consumers)
2. Refactor digitalmodel + worldenergydata in parallel (isolated worktrees)

This respects the dependency graph while maximizing parallelism where safe.

## Cross-Repo Shared Patterns

All three repos will converge on:

- **Packaging:** pyproject.toml-only (no setup.py), dependencies pinned with `>=min,<next_major`, optional deps in extras groups, `requires-python` consistent with classifiers and tool targets
- **Type hints:** Enforce `disallow_untyped_defs = true` in mypy, expand scope incrementally
- **Linting:** ruff + black + isort via pre-commit, mypy as CI blocker (not `|| true`)
- **Testing:** pytest with markers (unit, integration, slow), coverage gates, fixtures in `tests/fixtures/`
- **Logging:** loguru (already a dep in all 3), no raw print statements

---

## Phase 1: assetutilities (Sequential — Foundation Stabilization)

**Worktree:** Single isolated worktree from assetutilities repo.

### 1A. Packaging Hygiene

- Remove `pytest` from core `[project.dependencies]` → move to `[project.optional-dependencies.dev]`
- Pin all dependencies with upper bounds: `>=min,<next_major`
- Remove stale `setup.py` pass-through (pyproject.toml is the sole build config)
- Clean `MANIFEST.in` to include `docs/` and data files
- Reconcile black target (`py38-py311`) with `requires-python` (`>=3.9`) — update black to `py39-py312`

### 1B. Architecture — Decompose Monoliths

**agent_os/commands/ (5 files, 901-1099 LOC each):**
- `cli.py` (1071 LOC) → split into `subcommands/` directory, one file per command group
- `context_optimization.py` (1099 LOC) → extract merge, dedup, optimization into separate modules
- `specs_integration.py` (1026 LOC) → split loader, validator, merger
- `template_management.py` (1068 LOC) → split template operations
- `documentation_integration.py` (901 LOC) → extract generators

**common/data.py (1217 LOC, untyped, mypy-exempted):**
- Decompose into:
  - `common/readers/excel_reader.py` — ExcelReader class
  - `common/readers/csv_reader.py` — CSVReader class
  - `common/readers/__init__.py` — re-exports
  - `common/transform.py` — Transform class
  - `common/attribute_dict.py` — AttributeDict utility
- Remove mypy override for data.py once new modules are typed

### 1C. Code Quality

- Add type hints to all decomposed modules from 1B
- Add type hints to `common/database.py` (1150 LOC, currently untyped)
- Resolve 16 TODOs: delete stale ones, convert active to GitHub issues

### 1D. Cleanup

Delete stale root-level files:
- `GLOBAL_SETUP_COMPLETE.md`
- `GLOBAL_UV_ENVIRONMENT.md`
- `MANDATORY_SLASH_COMMAND_ECOSYSTEM.md`
- `DEPLOYMENT_SUMMARY.md`
- `TEST_PATH_RESOLUTION_FIX.md`
- `ENHANCED_AGENT_OS_RELEASE.md`
- `REQUIREMENTS_MIGRATION.md`
- `CLAUDE.md.backup-20251023-081047`

Remove empty directories:
- `.agent-runtime/`
- `.common-commands/`
- `.slash-commands/`
- `slash_commands/`
- `.command-backups/`

### 1-Gate: Success Criteria

- [ ] 0 stale root-level MD files
- [ ] `common/data.py` decomposed into typed modules
- [ ] mypy override for data.py removed
- [ ] All 1235 tests pass
- [ ] Clean pyproject.toml (no pytest in core deps, all pinned)

---

## Phase 2A: digitalmodel (Parallel — Worktree 1)

**Worktree:** Isolated worktree from digitalmodel repo. Launches after Phase 1 merges.

### 2A-1. Packaging Hygiene

Deduplicate 9 conflicting dependency entries:
- `assetutilities` — remove bare entry, keep `>=0.0.7`
- `pyyaml` — remove triple-spec (`pyyaml`, `>=6.0.0,<7.0.0`, `==6.0.1`), keep `>=6.0.0,<7.0.0`
- `dash`, `deepdiff`, `loguru`, `imgkit`, `kaleido` — deduplicate each

Move ~30 optional packages from core deps to extras groups:
- `[project.optional-dependencies.solvers]` — OrcFxAPI, gmsh
- `[project.optional-dependencies.viz]` — dash, kaleido, seaborn
- `[project.optional-dependencies.web]` — fastapi, uvicorn, sqlalchemy
- `[project.optional-dependencies.async]` — aiofiles, asyncpg, asyncio-mqtt

Fix version targeting:
- Reconcile `requires-python = ">=3.11"` with classifiers (drop 3.9/3.10 classifiers)
- Align `[tool.black]` and `[tool.mypy]` python_version with `>=3.11`

Delete stale root artifacts: `--version.cvg`, `--version.dat`, `--version.sta`

### 2A-2. Architecture — Decompose curves.py

`naval_architecture/curves.py` at 29,666 lines is the largest file across all 3 repos.

Split into subpackage `naval_architecture/curves/`:
- `__init__.py` — re-exports for backward compatibility
- One module per logical curve group (identify groups from class/function clustering)
- Target: every file < 500 LOC

Update `_compat.py` redirect layer if needed for backward compatibility.

Secondary decomposition targets (>1500 LOC):
- `infrastructure/base_solvers/well/wellpath3D.py` (1,985 LOC)
- `solvers/orcaflex/orcaflex_model_components.py` (1,899 LOC)

### 2A-3. Code Quality

Add type hints to zero-coverage solver entry points:
- `solvers/orcaflex/orcaflex.py` (0% type hints, 2 functions)
- `hydrodynamics/aqwa/aqwa_router.py` (0% type hints, 4 functions)

Add docstrings to zero-docstring modules (OrcaFlex, AQWA routers).

Triage 142 TODOs:
- Delete stale ones (e.g., "DELETE by 01 March 2024")
- Convert active ones to GitHub issues
- Keep legitimate inline notes

### 2A-4. Testing

- Fix/remove entries from 25+ `collect_ignore` list where root cause is addressable
- Verify 80%+ coverage maintained after all structural changes
- Run full test suite in worktree before merge

### 2A-Gate: Success Criteria

- [ ] 0 duplicate dependency entries in pyproject.toml
- [ ] `curves.py` split — every resulting file < 500 LOC
- [ ] Solver entry points (OrcaFlex, AQWA) have type hints
- [ ] 80%+ test coverage maintained
- [ ] All existing tests pass

---

## Phase 2B: worldenergydata (Parallel — Worktree 2)

**Worktree:** Isolated worktree from worldenergydata repo. Launches after Phase 1 merges.

### 2B-0. Data Resolver

**Problem:** 9.4GB of analysis data lives at `/mnt/ace/worldenergydata/data/` (2.7G bsee, 6.7G hse). Code uses 48+ hardcoded relative paths like `Path("data/modules/bsee")`. No centralized config. Data must not be committed to git.

**Solution:** Add `src/worldenergydata/common/data_resolver.py`

Resolution order:
1. `WED_DATA_ROOT` env var (explicit override)
2. Symlink at `<project_root>/data` → external mount (convention-based)
3. Fallback to `<project_root>/data/` as-is (development/CI default)

Public API:
- `get_data_root() -> Path` — resolve and cache the data root
- `get_module_data(module: str) -> Path` — e.g., `get_module_data("bsee")` returns resolved path to bsee data
- Raises `DataNotFoundError` with clear message if data unavailable

Setup script: `scripts/setup-data-link.sh`
- Creates symlink: `data/` → target (default `/mnt/ace/worldenergydata/data/`)
- Verifies expected subdirectories exist (`modules/bsee/`, `modules/hse/`)
- Idempotent — safe to re-run
- Accepts target path as argument for other machines

Git safety:
- Large data files stay in `.gitignore` (already partially configured)
- `data/.gitkeep` preserved so directory exists for fresh clones
- Small reference files (catalog, legacy inventories) that are already tracked stay

Machine portability:
| Machine | Configuration |
|---------|--------------|
| ace-linux (primary) | `WED_DATA_ROOT=/mnt/ace/worldenergydata/data` in `.env` or shell profile |
| CI/GitHub Actions | Small test fixtures in `tests/fixtures/` — no bulk data needed |
| Fresh clone | Run `scripts/setup-data-link.sh /path/to/data` |
| Windows | `set WED_DATA_ROOT=D:\worldenergydata\data` |

Migration: Replace all 48+ hardcoded `Path("data/...")` references with `data_resolver.get_module_data()` calls.

### 2B-1. Module Consolidation (Critical)

**Problem:** Both `/bsee/` (65K SLOC) and `/modules/bsee/` exist. Same for `/marine_safety/` (29K SLOC) vs `/modules/marine_safety/`.

**Strategy:**
1. Determine canonical location using MODULE_INDEX.md and MIGRATION_GUIDE.md (expected: `/modules/` is target structure)
2. Map every import chain before moving anything
3. Migrate to single location, update all imports
4. Update all test imports accordingly
5. Clean legacy directories: `common/legacy/`, `bsee/analysis/legacy/`, `modules/bsee/analysis/legacy/`

### 2B-2. Packaging Hygiene

- Replace `assetutilities @ git+https://...` with pinned version or editable local path (matching digitalmodel's `../assetutilities` pattern)
- Add upper bounds to all 65 loose `>=` dependencies
- Make mypy a CI blocker: remove `|| true` from CI workflow, expand mypy scope beyond `common/`

### 2B-3. Code Quality

- Replace 487 `print()` statements with `loguru` logging (`from worldenergydata.common.logging import get_logger`)
- Fix 49 bare `except:` blocks → catch specific exception types
- Add type hints to legacy BSEE modules (highest-traffic, worst coverage)

### 2B-4. Testing & Coverage

Priority coverage targets (currently 0%):
- `validation/schemas.py` (250 lines)
- `validation/base.py` (142 lines)
- `validators/data_validator.py` (123 lines)

Target: raise coverage from 19.17% → 40%+ (realistic for single refactor cycle).

Enable `pytest -n auto` for parallel test execution in CI.

### 2B-Gate: Success Criteria

- [ ] Single `bsee/` location (no duplication)
- [ ] Single `marine_safety/` location (no duplication)
- [ ] Data resolver in place, all hardcoded paths migrated
- [ ] `scripts/setup-data-link.sh` working
- [ ] 0 `print()` statements in source (all replaced with logging)
- [ ] Coverage ≥ 40% (up from 19.17%)
- [ ] mypy blocks CI (no `|| true`)

---

## Agent Team Composition

| Phase | Worktree | Agent | Scope |
|-------|----------|-------|-------|
| 1 | assetutilities | 1 gsd-executor | All 4 streams (1A-1D) sequentially |
| 2A | digitalmodel | 1 gsd-executor | Packaging + architecture + quality + testing |
| 2B | worldenergydata | 1 gsd-executor | Data resolver + consolidation + packaging + quality + coverage |

Phase 2A and 2B launch simultaneously after Phase 1 completes and merges.

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| assetutilities API changes break downstream | Phase 1 completes before Phase 2 starts; backward compat via re-exports |
| curves.py decomposition breaks imports | `_compat.py` redirect layer + `__init__.py` re-exports |
| worldenergydata module consolidation breaks 742 test files | Map all imports first; consolidation agent verifies test suite before committing |
| 9.4GB data not available in CI | Test fixtures in `tests/fixtures/`; `@pytest.mark.integration` for data-dependent tests |
| Coverage target (19% → 40%) too ambitious for single pass | Focus on validation layer (0%) first; 40% is stretch goal, 30% is minimum |
