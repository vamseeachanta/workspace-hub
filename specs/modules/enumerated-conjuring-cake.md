# Data Residence Strategy: worldenergydata ↔ digitalmodel

---
title: "Data Residence Strategy"
description: "Three-tier data governance across worldenergydata, digitalmodel, and project repos"
version: "2.0"
module: workspace-hub
session:
  id: enumerated-conjuring-cake
  agent: claude-opus-4.6
review:
  status: pending
  related: [WRK-096, WRK-097]
---

## Context

Engineering data is scattered across `worldenergydata` and `digitalmodel` with no formal governance. INVENTORY.md in worldenergydata claims hull geometry was "gathered from digitalmodel" (incorrect — worldenergydata is the collection source). SN curves are hardcoded as Python dicts in digitalmodel (37 curves across 4 standards, 799-line file). The `sn_curve_plotter.py` references a CSV at a path that doesn't exist (`data/fatigue/fatigue_curves_structured.csv` — the `data/` directory hasn't been created). Material properties sit in `src/digitalmodel/data_systems/data/steel_material.yml` buried inside the package tree. There's no single source of truth for "where does data live?"

**Parallel work**: WRK-096 is restructuring worldenergydata's Python module imports (code-only). Our changes to worldenergydata are data/docs-only (INVENTORY.md, CLAUDE.md), so no conflict on files — but CLAUDE.md has an existing merge conflict that must be resolved.

## Decision: Three-Tier Data Model

| Tier | What | Owner | Examples |
|------|------|-------|----------|
| **1 — Collection** | Raw data from external public sources | `worldenergydata` | BSEE, SODIR, metocean, vessel hulls, oil prices |
| **2 — Engineering Reference** | Standard lookup tables for analysis | `digitalmodel` | SN curves, steel grades, hydro coefficients |
| **3 — Project** | Project-specific inputs/outputs | project repos | Analysis configs, client deliverables |

**Boundary test**: "Where did this data originate?" Public source → Tier 1. Engineering standard → Tier 2. Specific project → Tier 3.

## Implementation Plan

### Phase 0: Policy Documents (no code risk)

**Create `docs/DATA_RESIDENCE_POLICY.md`** — canonical three-tier policy with boundary test and handoff contract.

**Create `ADR-004-data-residence-strategy.md`** — follows ADR-003 format exactly (YAML frontmatter with id, type, title, category, tags, repos, confidence, created, status, etc.)

- ADR-003 template: `.claude/knowledge/entries/decisions/ADR-003-import-knowledge-work-plugins.md`

### Phase 1: Fix worldenergydata references (docs only)

**1a. Edit `worldenergydata/data/modules/vessel_hull_models/INVENTORY.md`**
- Line 4: Change `> Source: Gathered from digitalmodel repository` → `> Source: Authoritative collection — hull geometry acquired from CAD exports, OrcaWave, and 3D model repositories`
- Lines 44-84: Rewrite "External Resources (digitalmodel)" section — remove hardcoded absolute paths (`/mnt/github/workspace-hub/digitalmodel/...`), replace with cross-references to the data_sources.yaml convention and generic tool descriptions
- Preserve all hull model metadata and acquisition status table unchanged

**1b. Resolve `worldenergydata/CLAUDE.md` merge conflict**
- Merge HEAD version (project-specific) with origin/main (detailed rules), keeping HEAD structure as primary
- Add one line: `Data governance: see workspace-hub docs/DATA_RESIDENCE_POLICY.md`
- **WRK-096 coordination**: If WRK-096 resolves the conflict first, just add our line

### Phase 2: Create digitalmodel data directory tree

```
digitalmodel/
├── data/                          # NEW — Tier 2 engineering reference data
│   ├── README.md                  # Data catalog + policy pointer
│   ├── fatigue/
│   │   └── sn_curves.yaml        # Externalized from sn_curves.py
│   └── materials/
│       └── steel_grades.yaml     # Moved from src/digitalmodel/data_systems/data/
```

- `digitalmodel/data/` does NOT exist yet — must create
- `digitalmodel/config/` already exists with domain subdirectories

### Phase 3: Externalize SN Curves (TDD — highest complexity)

**Current state** (`sn_curves.py:263-342`):
- `StandardSNCurves` class with class-level dicts: `DNV_CURVES` (14), `API_CURVES` (5), `BS_CURVES` (8), `AWS_CURVES` (8), `DNV_MULTISLOPE_CURVES` (2) = **37 curves total**
- `get_curve()` classmethod at line 344 returns `PowerLawSNCurve` from dict lookup
- `get_multislope_curve()` at line 391 returns `MultislopeSNCurve` (imported from `.analysis`)
- Existing tests: `tests/structural/fatigue/test_fatigue_migration.py` imports via `digitalmodel.fatigue` (compat layer)

**3a. Write pinning tests (TDD — Red then Green baseline)**

Create `tests/structural/fatigue/test_sn_curves_yaml.py`:
- Pin exact parameter values for all 37 curves (A, m, fatigue_limit)
- Pin all 2 multislope curves (slopes, constants, transition_cycles, fatigue_limit)
- Test `get_curve()` returns correct values for every standard/class combo
- Test `list_curves()` counts match
- Run against current code to confirm green baseline BEFORE any changes

**3b. Create `data/fatigue/sn_curves.yaml`**

```yaml
# SN Curve Parameters — Engineering Reference Data (Tier 2)
# Sources: DNV-RP-C203, API RP 2A, BS 7608, AWS D1.1
metadata:
  version: "1.0"
  tier: 2
  policy: "../../docs/DATA_RESIDENCE_POLICY.md"

standards:
  DNV:
    description: "DNV-RP-C203 (in air, T=16-25mm)"
    curves:
      B1: {A: 4.22e15, m: 4.0, fatigue_limit: 106.97}
      B2: {A: 1.01e15, m: 3.5, fatigue_limit: 93.59}
      # ... all 14 DNV curves
    multislope:
      D_MULTISLOPE:
        slopes: [3.0, 3.5, 5.0]
        constants: [5.73e11, 1.08e11, 2.5e10]
        transition_cycles: [2e6, 1e7]
        fatigue_limit: 52.63
      # ... F_MULTISLOPE
  API:
    description: "API RP 2A-WSD"
    curves:
      X: {A: 1.01e12, m: 3.0, fatigue_limit: 48.0}
      # ... all 5 API curves
  BS:
    description: "BS 7608"
    curves: # ... all 8 BS curves
  AWS:
    description: "AWS D1.1"
    curves: # ... all 8 AWS curves
```

**3c. Modify `sn_curves.py` — add YAML loader (~40 lines added)**

Key changes:
1. Add `import yaml` (with `try/except ImportError` for graceful degradation)
2. Add `_loaded_from_yaml: bool = False` class variable on `StandardSNCurves`
3. Add `_find_sn_data_file()` function: checks `DIGITALMODEL_DATA_DIR` env var, then `Path(__file__).parents[4] / "data" / "fatigue" / "sn_curves.yaml"` (repo root relative)
4. Add `_ensure_loaded()` classmethod: lazy-loads YAML on first call, overrides class dicts
5. Call `_ensure_loaded()` at start of `get_curve()` (line 345), `get_multislope_curve()` (line 392), `list_curves()` (line 436)
6. **Keep hardcoded dicts as fallback** — if YAML not found or yaml not installed, log warning and use existing dicts

Path resolution: `__file__` is at `src/digitalmodel/structural/fatigue/sn_curves.py`, so `.parents[4]` = `digitalmodel/` repo root where `data/` lives.

**3d. Run tests**
- `uv run pytest tests/structural/fatigue/test_sn_curves_yaml.py -v` (new pinning tests)
- `uv run pytest tests/structural/fatigue/test_fatigue_migration.py -v` (existing tests)

### Phase 4: Fix SN Curve Plotter broken path

**Current** (`sn_curve_plotter.py:37-39`):
```python
data_path = Path(__file__).parent.parent.parent.parent / "data" / "fatigue" / "fatigue_curves_structured.csv"
```

This resolves to `digitalmodel/data/fatigue/fatigue_curves_structured.csv` — the CSV doesn't exist.

**Fix**: Add graceful error handling — if CSV not found, raise `FileNotFoundError` with message explaining where to place the legacy 221-row CSV. The plotter is a separate legacy system from the `StandardSNCurves` library; we don't need to generate the CSV as part of this work item.

### Phase 5: Create `config/data_sources.yaml`

Declare external data dependencies in `digitalmodel/config/data_sources.yaml`:

```yaml
version: "1.0"
policy: "../docs/DATA_RESIDENCE_POLICY.md"  # Not yet present in digitalmodel; relative to workspace-hub
tier: 2

local_data:
  fatigue:
    sn_curves: {path: "data/fatigue/sn_curves.yaml", tier: 2}
  materials:
    steel_grades: {path: "data/materials/steel_grades.yaml", tier: 2}

external_dependencies:
  worldenergydata:
    vessel_hull_models:
      source_path: "worldenergydata/data/modules/vessel_hull_models/"
      type: read_only
      tier: 1
    metocean:
      source_path: "worldenergydata/data/metocean/"
      type: read_only
      tier: 1
```

No path resolver helper needed yet — this is a declaration file. Runtime resolution can be added when actual cross-repo data access code is written.

### Phase 6: Steel material move

**Current**: `src/digitalmodel/data_systems/data/steel_material.yml` (49 lines, 9 grades)
**Target**: `data/materials/steel_grades.yaml`

Steps:
1. TDD: Write test loading steel grades, validating all 9 grades match current values
2. Copy content to `data/materials/steel_grades.yaml` with improved metadata header
3. Keep original file as-is (backward compat for `pipe_properties.py` line 186 which uses `assetutilities.get_library_filename`)
4. Add deprecation comment to original file pointing to new canonical location

**Note**: Updating `pipe_properties.py` to use the new path is a separate concern — it depends on `assetutilities.get_library_filename()` which resolves relative to the package root (`src/digitalmodel/`), not the repo root. Changing that path resolution is out of scope for this work item.

### Phase 7: Documentation cross-references

- Add to `digitalmodel/CLAUDE.md`: `Data governance: see workspace-hub docs/DATA_RESIDENCE_POLICY.md`
- Add to `worldenergydata/CLAUDE.md` (done in Phase 1b)
- Create `digitalmodel/data/README.md` with tier explanation and file catalog

## Execution Order

```
Phase 0 (policy docs)  ─────────┐
Phase 1 (worldenergydata fixes) ─┤── parallel, no deps
                                  │
Phase 2 (create data/ dirs) ─────┤── after Phase 0
                                  │
Phase 3 (SN curve TDD) ──────────┤── after Phase 2
Phase 4 (plotter fix) ───────────┤── after Phase 2, parallel with 3
Phase 5 (data_sources.yaml) ─────┤── after Phase 0, parallel with 3
                                  │
Phase 6 (steel material) ────────┤── after Phase 2
Phase 7 (doc cross-refs) ────────┘── after Phase 0+1
```

## Files to Modify

| File | Action | Phase |
|------|--------|-------|
| `docs/DATA_RESIDENCE_POLICY.md` | **Create** | 0 |
| `.claude/knowledge/entries/decisions/ADR-004-data-residence-strategy.md` | **Create** | 0 |
| `worldenergydata/data/modules/vessel_hull_models/INVENTORY.md` | **Edit** — fix provenance | 1 |
| `worldenergydata/CLAUDE.md` | **Edit** — resolve conflict, add ref | 1 |
| `digitalmodel/data/README.md` | **Create** | 2 |
| `digitalmodel/data/fatigue/sn_curves.yaml` | **Create** — 37 curves | 3 |
| `digitalmodel/tests/structural/fatigue/test_sn_curves_yaml.py` | **Create** — pinning tests | 3 |
| `digitalmodel/src/digitalmodel/structural/fatigue/sn_curves.py` | **Edit** — add YAML loader | 3 |
| `digitalmodel/src/digitalmodel/structural/fatigue/sn_curve_plotter.py` | **Edit** — graceful error | 4 |
| `digitalmodel/config/data_sources.yaml` | **Create** | 5 |
| `digitalmodel/data/materials/steel_grades.yaml` | **Create** — copy from steel_material.yml | 6 |
| `digitalmodel/CLAUDE.md` | **Edit** — add ref | 7 |

## WRK-096 Coordination

| Our file | WRK-096 touches? | Conflict risk |
|----------|-------------------|---------------|
| INVENTORY.md | No (data file) | None |
| worldenergydata/CLAUDE.md | Possible (may resolve merge conflict) | Low — add our line after their resolve |
| All digitalmodel files | No (WRK-096 is worldenergydata only) | None |

**Strategy**: Execute Phase 1b (worldenergydata CLAUDE.md) last among worldenergydata changes. Check if WRK-096 has resolved the merge conflict. If yes, append our line. If no, resolve it ourselves.

## Verification

1. **SN curve integrity**: `uv run pytest tests/structural/fatigue/` in digitalmodel — all 37 curves load from YAML with values identical to hardcoded originals
2. **Existing tests pass**: `uv run pytest tests/structural/fatigue/test_fatigue_migration.py` — no regressions
3. **Policy reachable**: `ls ../../docs/DATA_RESIDENCE_POLICY.md` from within both submodules
4. **No circular refs**: `grep -r "digitalmodel" worldenergydata/data/` returns nothing after INVENTORY.md fix
5. **Fallback works**: Delete YAML temporarily, verify `StandardSNCurves.get_curve()` still works from hardcoded dicts
6. **Plotter graceful**: Instantiate `SNCurvePlotter()` without CSV, verify helpful `FileNotFoundError`

## Scope Exclusions

- **DATA_REORGANIZATION_PLAN.md full execution** (267 files) — only steel material and fatigue data. Vessels/hydrodynamic are separate WRK items
- **Runtime path resolver** for cross-repo data — declaration only via data_sources.yaml
- **`pipe_properties.py` path update** — depends on `assetutilities.get_library_filename` refactor
- **Legacy CSV generation** for plotter — separate data acquisition task
- **WRK-096 module restructure** — parallel, non-overlapping work
