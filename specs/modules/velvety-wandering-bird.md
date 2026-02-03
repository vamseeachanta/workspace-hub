---
title: "Restructure digitalmodel into grouped module architecture"
description: "Group 68 flat modules into ~11 domain clusters, add backward compat shim, create test/example/doc stubs for uncovered modules."
version: "3.0"
module: "digitalmodel"

session:
  id: "velvety-wandering-bird"
  agent: "claude-opus-4.5"

review:
  required_iterations: 3
  current_iteration: 1
  status: "in_review"
  legal_scan: "pass"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 1
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 1
      feedback: ""
  ready_for_next_step: false

status: "implemented"
progress: 95
priority: "high"
complexity: "very-complex"
tags: [architecture, refactoring, grouping, module-structure, backward-compat]

created: "2026-02-01"
updated: "2026-02-02"

links:
  spec: "specs/modules/velvety-wandering-bird.md"
  work_item: "WRK-066"
  pr_phases_7_11: "https://github.com/vamseeachanta/digitalmodel/pull/130"
  pr_phases_12_18: "https://github.com/vamseeachanta/digitalmodel/pull/131"
  branch: "refactor/wrk-066-group-modules"
---

# Restructure digitalmodel into Grouped Module Architecture

## Completed Work (PR #130)

Phases 0-6 (src/ flattening) and Phases 7-11 (tests/examples/scripts cleanup) are done. All 68 modules now live flat under `digitalmodel.X`. PR #130 merged 962 files.

---

## Current Problem

68 flat modules under `src/digitalmodel/` is too many to navigate. No domain grouping exists. 30+ modules have zero tests, docs, or examples.

| Metric | Value |
|--------|-------|
| Total src modules | 68 |
| Modules with tests | 37 (54%) |
| Modules with examples | 11 (16%) |
| Modules with docs | ~25 (37%) |
| Modules with ALL three | 4 (6%) |
| Modules with NONE | 30 (44%) |

---

## Plan: 11 Module Groups

### Group Assignments

```
src/digitalmodel/
  solvers/              # Simulation & numerical tools
    orcaflex/           # 190 files, 49.7K lines — LARGEST
    orcawave/
    orcaflex_browser/
    orcaflex_post_process/
    fea_model/
    gmsh_meshing/
    blender_automation/

  hydrodynamics/        # Wave & fluid mechanics
    aqwa/
    diffraction/
    hydrodynamics/      # -> digitalmodel.hydrodynamics.hydrodynamics (accepted)
    rao_analysis/
    bemrosetta/

  structural/           # Strength, fatigue, pipe capacity
    fatigue/
    fatigue_analysis/
    stress/
    structural_analysis/
    pipe_capacity/
    pipe_cross_section/
    analysis/           # Wall thickness, plate capacity (API STD)

  subsea/               # Riser, mooring, pipeline
    mooring_analysis/
    catenary/
    catenary_riser/
    vertical_riser/
    viv_analysis/
    pipeline/

  marine_ops/           # Marine operations & production
    marine_analysis/
    marine_engineering/
    ct_hydraulics/
    reservoir/
    artificial_lift/

  signal_processing/    # Signal & time series
    signal_analysis/
    time_series/

  infrastructure/       # Core framework & utilities
    common/
    core/
    config/
    base_configs/
    base_solvers/
    services/
    domains/
    validation/
    validators/
    templates/
    calculations/
    transformation/

  data_systems/         # Data acquisition & management
    data/
    data_manager/
    data_procurement/
    data_scraping/
    pyintegrity/

  workflows/            # Automation & AI
    automation/
    workflow_automation/
    ai_workflows/
    agents/
    mcp_server/
    skills/

  visualization/        # Rendering & reports
    visualization/      # -> digitalmodel.visualization.visualization (accepted)
    reporting/
    design_tools/

  specialized/          # Domain-specific niche modules
    gis/
    digitalmarketing/
    finance/
    project_management/
    rigging/
    custom/
    api_analysis/
    cli/

  # STAY AT ROOT (not grouped):
  legacy/               # Historical code, compat-only
  modules/              # MetaPathFinder compat shim
  __init__.py
  __main__.py
  engine.py
  _compat.py
  diffraction_cli.py
  standards_lookup.py
```

**Total**: 11 groups, 67 modules distributed. `legacy/` and `modules/` stay at root.

### Naming Collisions Resolved

| Collision | Resolution |
|-----------|-----------|
| Group `analysis/` vs module `analysis` | Group renamed to `signal_processing/`; module stays `analysis` inside `structural/` |
| Group `automation/` vs module `automation` | Group renamed to `workflows/` |
| Group `data/` vs module `data` | Group renamed to `data_systems/` |
| Group `core/` vs module `core` | Group renamed to `infrastructure/` |
| `hydrodynamics.hydrodynamics` | Accepted — common pattern |
| `visualization.visualization` | Accepted — common pattern |

---

## Backward Compatibility Architecture

Three import layers must all work after this change:

```
Layer 1 (oldest): digitalmodel.modules.X.Y   -> compat shim (existing)
Layer 2 (current): digitalmodel.X.Y          -> new compat shim
Layer 3 (new):     digitalmodel.<group>.X.Y   -> canonical path
```

### Implementation: Dual mechanism

**1. `__getattr__` on `src/digitalmodel/__init__.py`** — catches `from digitalmodel import X` and `from digitalmodel.X import Y`:

```python
_FLAT_TO_GROUP = {
    "orcaflex": "solvers",
    "aqwa": "hydrodynamics",
    "fatigue": "structural",
    # ... all 67 mappings
}

def __getattr__(name):
    if name in _FLAT_TO_GROUP:
        import importlib
        return importlib.import_module(f"digitalmodel.{_FLAT_TO_GROUP[name]}.{name}")
    raise AttributeError(f"module 'digitalmodel' has no attribute {name!r}")
```

**2. `_GroupRedirectFinder` in `_compat.py`** — catches `import digitalmodel.X.submod` (path traversal):

```python
class _GroupRedirectFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        parts = fullname.split(".")
        if len(parts) >= 2 and parts[0] == "digitalmodel":
            top = parts[1]
            if top in _FLAT_TO_GROUP:
                group = _FLAT_TO_GROUP[top]
                new = f"digitalmodel.{group}.{'.'.join(parts[1:])}"
                return importlib.util.find_spec(new)
        return None
```

**Layer 1 chains automatically**: Existing `digitalmodel.modules.X` -> `digitalmodel.X` -> `digitalmodel.<group>.X`.

---

## Implementation Phases

### Phase 12: Safety Net (no file moves)

- [ ] Write `_FLAT_TO_GROUP` mapping registry in `_compat.py`
- [ ] Write compat tests: `tests/compat/test_group_compat.py` testing all 3 import layers
- [ ] Create group scaffold: 11 `__init__.py` files (empty, importable)
- [ ] Write migration script: `scripts/migrate_to_groups.py`

**Files**: ~15 created, 2 modified | **Risk**: Low

### Phase 13: Install Compat Shim (before any moves)

- [ ] Add `_GroupRedirectFinder` to `_compat.py`
- [ ] Add `__getattr__` to `src/digitalmodel/__init__.py`
- [ ] Register finder in `sys.meta_path` at package init
- [ ] Run full test suite — shim is no-op (modules haven't moved)

**Files**: 3 modified | **Risk**: Low (finder only activates for missing paths)

### Phase 14: Move Modules in 6 Batches

Each batch: `git mv` modules, update pyproject.toml entry points, run tests.

| Batch | Groups | Modules | CLI Entry Points | Risk |
|-------|--------|---------|------------------|------|
| 14a | `signal_processing/` + `visualization/` | 5 | signal-analysis | Low |
| 14b | `specialized/` + `data_systems/` | 13 | 0 | Low |
| 14c | `subsea/` | 6 | mooring-analysis, viv-analysis, catenary-riser | Medium |
| 14d | `hydrodynamics/` + `marine_ops/` | 10 | aqwa, diffraction, hydrodynamics, bemrosetta | Medium |
| 14e | `structural/` + `infrastructure/` | 19 | structural-analysis | High |
| 14f | `solvers/` + `workflows/` | 14 | 6 orcaflex CLIs, create-go-by, workflow-automation | High |

**Total**: ~1,200 files moved | **Risk**: Medium-High (compat shim mitigates)

### Phase 15: Update Critical Internal Imports (hybrid)

Update eagerly (not relying on shim):
- [ ] `engine.py` — 27 cross-module imports
- [ ] `__init__.py` — package-level re-exports
- [ ] `__main__.py` — entry point
- [ ] `pyproject.toml` — all 18 CLI entry points

Leave remaining ~190 files on compat shim for now. Migrate opportunistically.

**Files**: ~25 modified | **Risk**: Medium

### Phase 16: Add Test/Example/Doc Stubs

For each of the 30+ modules with no coverage:

**Test stub** (`tests/<group>/<module>/test_<module>_smoke.py`):
```python
def test_module_importable():
    import digitalmodel.<group>.<module>

def test_compat_import():
    import digitalmodel.<module>  # backward compat
```

**Example stub** (`examples/<group>/<module>/basic_usage.py`):
```python
"""Basic usage example for digitalmodel.<group>.<module>."""
# TODO: Add working example
```

**Doc stub** (`docs/modules/<group>/<module>/README.md`):
```markdown
# <module>
> Part of `digitalmodel.<group>`
## Overview
TODO: Module description
```

**Files**: ~350 new files | **Risk**: Low (purely additive)

### Phase 17: Mirror tests/ and examples/ Structure

Move test and example directories to match grouped layout:

```
tests/solvers/orcaflex/       (was tests/orcaflex/)
tests/hydrodynamics/aqwa/     (was tests/aqwa/)
tests/structural/fatigue/      (was tests/fatigue/)
...
```

Same for examples/.

**Files**: ~500 moved | **Risk**: Medium

### Phase 18: Final Verification

- [ ] `grep -r "digitalmodel\.modules\."` — only compat layer
- [ ] `grep -r "from digitalmodel\.[a-z]" --include="*.py"` in src/ — only compat shim + engine.py
- [ ] All 18 CLI entry points resolve
- [ ] `uv run pytest` passes
- [ ] Import all 67 modules via all 3 layers in a test

---

## Critical Files

| File | Role | Risk |
|------|------|------|
| `src/digitalmodel/_compat.py` | Both compat shims live here | HIGH — must handle 2 redirect layers |
| `src/digitalmodel/__init__.py` | `__getattr__` for flat->group redirect | HIGH — package entry point |
| `src/digitalmodel/engine.py` | 27 cross-module imports | HIGH — central dispatcher |
| `pyproject.toml` | 18 CLI entry points | MEDIUM — must update paths |
| `src/digitalmodel/modules/__init__.py` | Layer 1 compat (existing, DO NOT MODIFY) | LOW — already working |
| `tests/compat/test_restructure_compat.py` | Existing 30 compat tests | LOW — extend, don't break |

---

## File Impact Estimate

| Phase | Modified | Created | Moved | Total |
|-------|----------|---------|-------|-------|
| 12: Safety net | 2 | 15 | 0 | 17 |
| 13: Compat shim | 3 | 0 | 0 | 3 |
| 14: Move modules | 2 | 11 | ~1,200 | ~1,213 |
| 15: Update imports | 25 | 0 | 0 | 25 |
| 16: Add stubs | 0 | ~350 | 0 | 350 |
| 17: Mirror tests | 5 | 0 | ~500 | 505 |
| 18: Verification | 0 | 0 | 0 | 0 |
| **Total** | **~37** | **~376** | **~1,700** | **~2,113** |

---

## Verification Strategy

After each phase:
1. `uv run pytest tests/compat/` — all compat tests pass
2. `uv run python -c "import digitalmodel; print(digitalmodel.__version__)"` — package loads
3. After Phase 14 (each batch): `uv run pytest` — full suite
4. After Phase 18: verify all 3 import layers work for all 67 modules

---

## Open Questions

1. **`orcaflex` decomposition**: At 190 files / 49.7K lines, should `orcaflex` be further split within `solvers/`? (Out of scope for this plan — separate work item)
2. **`common` cleanup**: At 49 files / 20K lines, `common` is a grab-bag. Should it be split across groups? (Out of scope — separate work item)
3. **Deprecation timeline**: When do we remove the flat import compat shim? Suggest: after 2 minor version releases with deprecation warnings.

---

## Progress Tracker

| Phase | Status | PR |
|-------|--------|-----|
| 0-6: src/ flattening | Done | PR #129 |
| 7-11: tests/examples cleanup | Done | PR #130 |
| 12: Safety net | Done | PR #131 |
| 13: Compat shim | Done | PR #131 |
| 14: Move modules (6 batches) | Done | PR #131 |
| 15: Update imports | Done | PR #131 |
| 16: Add stubs | Done | PR #131 |
| 17: Mirror tests/examples | Done | PR #131 |
| 18: Final verification | Done | PR #131 |

## Actual Impact (PR #131)

| Metric | Planned | Actual |
|--------|---------|--------|
| Files changed | ~2,113 | 2,564 |
| Insertions | — | 3,204 |
| Deletions | — | 1,788 |
| Commits | 7 | 12 |
| Compat tests | 45 | 45/45 pass |
| Full suite | — | 1,555 pass, 100 pre-existing failures |
| Legal scan | — | Pass |

## Cross-Review (Iteration 1/3)

### Review Prompt for OpenAI Codex / Google Gemini

**PR**: https://github.com/vamseeachanta/digitalmodel/pull/131
**Branch**: `refactor/wrk-066-group-modules` (12 commits, 2,564 files changed)

**What changed**: Restructured 66 flat modules into 11 domain groups with 3-layer backward compatibility.

**Key review areas**:
1. **`_compat.py`** — `_GroupRedirectFinder` MetaPathFinder correctness: recursion guards, spec resolution, deprecation warnings
2. **`__init__.py`** — `__getattr__` interaction with `_GroupRedirectFinder` (double-redirect risk?)
3. **Group assignments** — Are the 11 groups logically coherent? Any modules misplaced?
4. **Name collisions** — `hydrodynamics.hydrodynamics` and `visualization.visualization` patterns
5. **Performance** — Does the MetaPathFinder add measurable import latency?
6. **Deprecation strategy** — Is the compat shim sufficient for a 2-release deprecation window?
7. **Test coverage** — 45 compat tests cover the shim; are edge cases (circular imports, lazy imports) tested?
