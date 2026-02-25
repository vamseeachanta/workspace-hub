# Plan: God Object Splits — Domain-by-Domain (Parallel)

**Strategy**: Domain-by-domain, both repos in parallel (user confirmed)
**Repos in scope**: `digitalmodel` (hydrodynamics/diffraction), `worldenergydata` (safety_analysis/taxonomy)
**Evidence basis**: Explore agent audit of top P1 candidates per `/clean-code` skill
**Constraint**: digitalmodel uses git plumbing for commits (4.2GB pack files hang `git commit`)

---

## Context

The `/clean-code` skill (v1.0.0) defines a 400-line hard limit and P1-P4 triage. Explore agents
confirmed the top P1 God Objects in both repos. These files have 5-7× the 400-line hard limit,
mix 3-5 distinct responsibilities, and see active development (confirmed via git log Feb 2026).

**Key findings from agent audit**:
- `worldenergydata/cost/data_collection/public_dataset.py` (1,643L) is a DATA file (95% raw
  dict records) — NOT a God Object, skip it
- `worldenergydata/well_production_dashboard/well_production.py` (1,090L) is already modular
  within an 18-file domain — skip it
- The 3 files below are genuine God Objects with clear, natural split boundaries

---

## File Creation Order (dependency-safe sequence)

### worldenergydata Target 1
1. `activity_definitions.py` — no project deps
2. `activity_registry.py` — imports `activity_definitions`
3. Replace `activity_taxonomy.py` with shim
4. Update `__init__.py`
5. Update callers (`incident_classifier.py`, `cli.py`, test file) to import from new paths directly (avoids DeprecationWarning noise in test output)

### digitalmodel Target 2
1. `report_data_models.py` — no project deps; owns `DOF_NAMES`, `DOF_UNITS`, `LOAD_RAO_UNITS`, `_find_closest_idx`, `_round_2d`
2. `report_computations.py` — imports `report_data_models`
3. `report_extractors.py` — imports `report_data_models` + `report_computations`; owns `extract_report_data_from_owr()` AND `build_report_data_from_solver_results()`
4. `report_builders.py` — imports `report_data_models` + `report_computations`; owns all 14 `_build_*_html()`, `HULL_TYPE_NOTES`, `_get_hull_type_note()`. Note: `_find_closest_idx` moves to `report_data_models` not here — `report_builders.py` imports it from there
5. Replace `report_generator.py` with shim + orchestration (keeps `generate_diffraction_report()` and `generate_report_from_owr()` bodies)

### digitalmodel Target 3
1. `benchmark_helpers.py` — no project deps; owns `DOF_ORDER`, `_AMPLITUDE_UNITS`, `_SOLVER_STYLES`, `_NEGLIGIBLE_AMPLITUDE_RATIO`, `_is_phase_at_negligible_amplitude()`, `_parse_fdf_panels()`, `_FILE_DESCRIPTIONS` (moved from class attr at line 1247)
2. `benchmark_rao_plots.py` — imports `benchmark_helpers`; extracted `_add_solver_traces_impl(plotter, fig, dof, ..., heading_x_axis)` — all 8 call sites must pass `self._heading_x_axis` explicitly
3. `benchmark_correlation.py` — imports `benchmark_helpers`
4. `benchmark_input_reports.py` — imports `benchmark_helpers`; `build_semantic_equivalence_html` nested closure `_render_diff_table` must be inlined (captures `parts` by reference — cannot be naively moved out of the outer function)
5. Refactor `benchmark_plotter.py` to orchestrator + thin wrappers; add imports from all 4 new modules; re-export `DOF_ORDER`, `_SOLVER_STYLES` at module level for any external callers

---

## Target 1: `worldenergydata` — `safety_analysis/taxonomy/activity_taxonomy.py` (1,550L)

**Agent verdict**: EXCELLENT candidate — clearest split boundary, fewest callers, existing test coverage

### Current Structure

- 3 classes: `Subactivity` (dataclass), `Activity` (dataclass), `ActivityTaxonomy` (registry)
- 19 `_build_*_activity()` builder functions (pure configuration, no logic coupling)
- 5 private index builders + 5 public finder methods on `ActivityTaxonomy`

### Callers (verified by agent)

- `safety_analysis/taxonomy/incident_classifier.py` — imports `ActivityTaxonomy`
- `safety_analysis/taxonomy/cli.py` — imports `ActivityTaxonomy`
- `safety_analysis/taxonomy/__init__.py` — re-exports `ActivityTaxonomy`

Zero callers outside the taxonomy subpackage. Shim = 3 re-export lines.

### Proposed Split (3 modules)

| New Module | Est. Lines | Responsibility | Key Contents |
|-----------|-----------|---------------|-------------|
| `activity_definitions.py` | ~1,200 | Data models + 19 builder functions | `Subactivity`, `Activity` dataclasses; all `_build_*_activity()` functions — pure data, no registry imports |
| `activity_registry.py` | ~280 | Registry + index management | `ActivityTaxonomy.__init__()`, 5 `_build_*_index()` methods, 5 `find_by_*()` public methods |
| `activity_queries.py` | ~50 | Convenience query API | `get_activity()`, `get_activity_codes()`, `summary()` (may merge into registry) |

**Import order** (no circular deps):
`activity_definitions` → `activity_registry` (imports `Activity` from definitions) → `activity_queries`

### `activity_taxonomy.py` post-split (DeprecationWarning shim, ~15 lines)

```python
"""Deprecated: import from activity_definitions or activity_registry directly."""
import warnings
warnings.warn("activity_taxonomy is split; see activity_definitions/activity_registry",
              DeprecationWarning, stacklevel=2)
from .activity_definitions import Subactivity, Activity  # noqa: F401,F403
from .activity_registry import ActivityTaxonomy  # noqa: F401
__all__ = ["Subactivity", "Activity", "ActivityTaxonomy"]
```

### `__init__.py` update

```python
from .activity_definitions import Subactivity, Activity
from .activity_registry import ActivityTaxonomy
```

**Verification**: `python3 -m pytest worldenergydata/tests/safety_analysis/taxonomy/ -q` — 252-line test file covers 14 activity types; must stay green before and after.

---

## Target 2: `digitalmodel` — `report_generator.py` (2,034L)

**Agent verdict**: 5 distinct responsibility groups; lazy-imported by only `benchmark_runner.py`

### Current Structure

1. **Data models** (lines 106–260): 5 Pydantic/dataclass models + DOF constants
2. **OrcaWave extraction** (lines 265–435): parses `.owr` diffraction output → models
3. **Physics computations** (lines 435–710): stability, natural periods, coupling, warnings
4. **HTML section builders** (lines 998–1900): 14 `_build_*_html()` functions + HULL_TYPE_NOTES
5. **Orchestration** (lines 1951–2034): `generate_diffraction_report()`, `generate_report_from_owr()`

### Callers (verified by agent)

- `benchmark_runner.py` — lazy imports inside `_generate_html_report()` (lines 518, 547)
- `test_report_generator.py` — tests computation functions; no HTML builder tests

### Proposed Split (4 new modules in `diffraction/`)

| New Module | Est. Lines | Responsibility |
|-----------|-----------|---------------|
| `report_data_models.py` | ~260 | `HydrostaticData`, `RollDampingData`, `LoadRAOData`, `MeshQualityData`, `DiffractionReportData`, `DOF_NAMES`, `DOF_UNITS`, `LOAD_RAO_UNITS` |
| `report_extractors.py` | ~180 | `extract_report_data_from_owr()`, `build_report_data_from_solver_results()`, `_round_2d()` |
| `report_computations.py` | ~280 | `compute_stability()`, `compute_radii_of_gyration()`, `compute_natural_periods()`, `compute_peak_responses()`, `compute_coupling_significance()`, `generate_executive_warnings()`, `_find_closest_idx()` |
| `report_builders.py` | ~1,200 | All 14 `_build_*_html()` functions, `HULL_TYPE_NOTES`, `_get_hull_type_note()`, `_AMPLITUDE_UNITS` |

**`report_generator.py` post-split** (shim + orchestration, ≤300L):
```python
from .report_data_models import (
    HydrostaticData, RollDampingData, LoadRAOData,
    MeshQualityData, DiffractionReportData, DOF_NAMES, DOF_UNITS, LOAD_RAO_UNITS,
)
from .report_extractors import extract_report_data_from_owr, build_report_data_from_solver_results
from .report_computations import (
    compute_stability, compute_radii_of_gyration, compute_natural_periods,
    compute_peak_responses, compute_coupling_significance, generate_executive_warnings,
)
from .report_builders import HULL_TYPE_NOTES

# Orchestration only — assemble sections from report_builders into final HTML
def generate_diffraction_report(...): ...
def generate_report_from_owr(...): ...

__all__ = [...]  # all exported names for backward compat
```

**Circular import guard**: `report_builders.py` imports `DiffractionReportData` from
`report_data_models` only — does NOT import from `report_computations` or `report_extractors`.

**Verification**: `python3 -m pytest digitalmodel/tests/hydrodynamics/diffraction/test_report_generator.py -q`

**Commit method**: git plumbing (4.2GB packs)
```bash
TREE=$(git write-tree)
COMMIT=$(git commit-tree "$TREE" -p HEAD -m "refactor: split report_generator.py into 4 focused modules")
git update-ref HEAD "$COMMIT"
```

---

## Target 3: `digitalmodel` — `benchmark_plotter.py` (2,700L)

**Agent verdict**: Single 2,700-line class `BenchmarkPlotter` with 8 responsibility groups; 7 callers in `benchmark_runner.py`

### Responsibility Groups Identified

1. **RAO amplitude/phase overlays** — `plot_amplitude_overlay()`, `plot_phase_overlay()`, `plot_difference_grid()` (~600L)
2. **Pairwise correlation + DOF analysis** — `plot_pairwise_correlations()`, `build_dof_report_sections()`, `_build_dof_commentary()` (~400L)
3. **Mesh schematic + input file HTML** — `build_mesh_schematic_html()`, `_parse_fdf_panels()`, `build_input_files_html()`, `build_input_comparison_html()` (~400L)
4. **Shared config + utilities** — `_SOLVER_STYLES`, `DOF_ORDER`, `_AMPLITUDE_UNITS`, `_get_solver_style()`, `_get_x_values()` (~200L)
5. **Stays in `BenchmarkPlotter`** — `build_hydro_coefficients_html()` (~150L), `build_raw_rao_data_html()` (~100L), `plot_all()`, `plot_per_dof()`, `__init__()` (~250L total)

### Proposed Split (4 new modules in `diffraction/`)

| New Module | Est. Lines | Key Contents |
|-----------|-----------|-------------|
| `benchmark_helpers.py` | ~200 | `_SOLVER_STYLES`, `DOF_ORDER`, `_AMPLITUDE_UNITS`, shared utils |
| `benchmark_input_reports.py` | ~400 | `build_mesh_schematic_html()`, `_parse_fdf_panels()`, `build_input_files_html()` |
| `benchmark_rao_plots.py` | ~600 | `plot_amplitude_overlay()`, `plot_phase_overlay()`, `plot_difference_grid()`, heading/axis helpers |
| `benchmark_correlation.py` | ~400 | `plot_pairwise_correlations()`, `build_dof_report_sections()`, `_build_dof_commentary()` |

**Refactor pattern**: `BenchmarkPlotter` methods become thin wrappers that call extracted module-level
functions, passing `self` data as arguments (composition, avoids self-reference loops):

```python
# benchmark_plotter.py post-split (≤400L)
from .benchmark_helpers import _SOLVER_STYLES, DOF_ORDER
from .benchmark_rao_plots import plot_amplitude_overlay as _plot_amplitude
from .benchmark_correlation import plot_pairwise_correlations as _plot_pairwise
from .benchmark_input_reports import build_mesh_schematic_html as _build_mesh

class BenchmarkPlotter:
    def plot_amplitude_overlay(self, ...):
        return _plot_amplitude(self._data, self._config, ...)
    ...
```

**Verification**: `python3 -m pytest digitalmodel/tests/hydrodynamics/diffraction/test_benchmark_plotter.py -q`

**Commit method**: git plumbing (same as Target 2)

---

## Plan Agent Findings (P1 gaps — integrated)

**Risk agent identified 5 HIGH/MEDIUM gaps requiring plan changes:**

1. **`DOF_NAMES` missing from shim `__all__`** — `test_report_generator.py` line 15 imports `DOF_NAMES` directly; shim must name it explicitly
2. **`build_report_data_from_solver_results` placement** — plan didn't assign it; belongs in `report_extractors.py` (calls `extract_report_data_from_owr` + uses `DOF_NAMES`)
3. **`_heading_x_axis` not passed to extracted `_add_solver_traces`** — 8 call sites need `self._heading_x_axis` explicitly; silent failure if missed
4. **Nested `_render_diff_table` closure** in `build_semantic_equivalence_html` captures `parts` by reference — cannot be naively extracted; must be inlined in the extracted function body
5. **`_FILE_DESCRIPTIONS` class attr** (line 1247, BenchmarkPlotter) — unreachable after `build_input_files_html` extraction; must move to `benchmark_helpers.py` as module constant

**Implementation agent identified 1 critical missing step:**

6. **`__pycache__` purge before tests** — after writing shim files, stale `.pyc` files may serve old bytecode; delete before test run

All 6 gaps are addressed in the Safety Protocol and per-target notes below.

---

## Scope Decisions (Codex review — frozen)

- `activity_queries.py`: **MERGED into `activity_registry.py`** — 50 lines does not warrant a separate module; `get_activity()`, `get_activity_codes()`, `summary()` move to `ActivityTaxonomy` class
- Split count: worldenergydata = **2 new modules** (definitions + registry), digitalmodel = **4 + 4 new modules**
- DeprecationWarning on shims: **once-per-session** (default Python `warnings.warn` behavior, no `stacklevel` changes to test output)
- Backward-compat contract duration: **one release cycle** (until next major tag; shim files marked `# remove after v<next>`; not enforced in scope of this WRK)

---

## Constants Ownership Policy (Codex P2)

One module owns constants; all others import from that owner only — no duplication.

| Domain | Constants Owner | Key Constants |
|--------|----------------|--------------|
| `report_generator` split | `report_data_models.py` | `DOF_NAMES`, `DOF_UNITS`, `LOAD_RAO_UNITS` |
| `report_builders` split | `report_builders.py` | `HULL_TYPE_NOTES`, `_AMPLITUDE_UNITS` |
| `benchmark_plotter` split | `benchmark_helpers.py` | `_SOLVER_STYLES`, `DOF_ORDER` |
| `activity_taxonomy` split | `activity_definitions.py` | All activity type constants, keyword sets |

Rule: if two new modules need the same constant, it lives in the "lower" module (fewer deps) and is imported upward.

---

## Acceptance Criteria Per Target (Codex P1)

### All targets (minimum gate before commit)

```bash
# 1. Baseline test count recorded before any changes
python3 -m pytest <domain-tests>/ -q 2>&1 | tail -3  # save N tests pass

# 2. Import surface unchanged — old import paths must resolve
python3 -c "
from <original_module> import <all_symbols_in___all__>
print('backward-compat: OK')
"

# 3. No new circular imports
python3 -c "import <package>; print('package import: OK')"

# 4. Importer smoke test — each direct caller still works
python3 -c "import <each_importer_module>; print('importer: OK')"

# 5. Post-split test count matches baseline
python3 -m pytest <domain-tests>/ -q 2>&1 | tail -3
```

### worldenergydata `activity_taxonomy.py`

```bash
# Importer smoke tests (all 3 callers)
python3 -c "from worldenergydata.safety_analysis.taxonomy.incident_classifier import *; print('OK')"
python3 -c "from worldenergydata.safety_analysis.taxonomy.cli import *; print('OK')"
python3 -c "from worldenergydata.safety_analysis.taxonomy import ActivityTaxonomy; print('OK')"
# Backward-compat via shim
python3 -c "from worldenergydata.safety_analysis.taxonomy.activity_taxonomy import ActivityTaxonomy, Activity, Subactivity; print('shim: OK')"
# Domain test baseline
python3 -m pytest worldenergydata/tests/safety_analysis/taxonomy/ -q
```

### digitalmodel `report_generator.py`

```bash
# All public symbols still importable from original path
python3 -c "
from digitalmodel.hydrodynamics.diffraction.report_generator import (
    HydrostaticData, RollDampingData, LoadRAOData, MeshQualityData, DiffractionReportData,
    extract_report_data_from_owr, build_report_data_from_solver_results,
    compute_stability, compute_radii_of_gyration, compute_natural_periods,
    compute_peak_responses, compute_coupling_significance, generate_executive_warnings,
    generate_diffraction_report, generate_report_from_owr, HULL_TYPE_NOTES,
)
print('backward-compat: OK')
"
# Importer smoke test (benchmark_runner lazy-imports only)
python3 -c "from digitalmodel.hydrodynamics.diffraction.benchmark_runner import BenchmarkRunner; print('benchmark_runner: OK')"
# Domain tests
PYTHONPATH=digitalmodel/src python3 -m pytest digitalmodel/tests/hydrodynamics/diffraction/test_report_generator.py -q
```

### digitalmodel `benchmark_plotter.py`

```bash
# All callers of BenchmarkPlotter still work
python3 -c "from digitalmodel.hydrodynamics.diffraction.benchmark_plotter import BenchmarkPlotter; print('OK')"
python3 -c "from digitalmodel.hydrodynamics.diffraction import BenchmarkPlotter; print('__init__ re-export: OK')"
# Domain tests
PYTHONPATH=digitalmodel/src python3 -m pytest digitalmodel/tests/hydrodynamics/diffraction/test_benchmark_plotter.py -q
# benchmark_runner behavior unchanged — functional smoke (does not require OrcaFlex license)
python3 -c "from digitalmodel.hydrodynamics.diffraction.benchmark_runner import BenchmarkRunner; r = BenchmarkRunner.__new__(BenchmarkRunner); print('instantiation: OK')"
```

---

## Execution Order

```
Phase 1: worldenergydata activity_taxonomy.py → 2 modules (lowest risk, fewest callers)
Phase 2: digitalmodel report_generator.py → 4 modules (well-isolated, lazy-loaded)
Phase 3: digitalmodel benchmark_plotter.py → 4 modules (most complex, do after Phase 2)
```

---

## WRK Items to Create

| WRK | Title | Route | Computer |
|-----|-------|-------|---------|
| WRK-NEW-G1 | Split `activity_taxonomy.py` into 2 focused modules | B | ace-linux-1 |
| WRK-NEW-G2 | Split `report_generator.py` into 4 focused modules | B | ace-linux-1 |
| WRK-NEW-G3 | Split `benchmark_plotter.py` into 4 focused modules | B | ace-linux-1 |

**Route B steps**: Explore (done) → Implement → Test → Archive

---

## Refactor Safety Protocol (per `/clean-code` skill, Codex P1/P2 + Plan agent hardened)

### Before any split

1. Record baseline: `python3 -m pytest <domain-tests>/ -q 2>&1 | tail -3` → save pass count
2. Map all callers: `grep -r "from <module> import\|import <module>" src/ tests/` → list every import site
3. Snapshot `__all__` from original file (or derive it from all public names)

### During split

4. Create all new submodules in dependency order (write only — zero deletions at this stage)
5. Verify no circular imports: `python3 -c "import <pkg>.<new_submodule>"` for each new file
6. Verify constants ownership: each constant name appears in exactly one new module
7. Replace original file with shim + DeprecationWarning

### After split (gate before commit)

8. **Purge stale `.pyc` files** (plan agent gap #6 — prevents stale bytecode serving old symbols):
   ```bash
   find <repo>/src/<pkg>/path/to/__pycache__/ -name "<original_module>*.pyc" -delete
   # Or: PYTHONDONTWRITEBYTECODE=1 for entire session
   ```
9. Run acceptance criteria commands from section above — all must pass
10. Run baseline test suite — pass count must match
11. Run one importer smoke test per caller — each must pass

### Commit

**worldenergydata** (normal commit, bypass hooks):
```bash
git add <files>
git -c core.hooksPath=/dev/null commit -m "refactor(wrk-NNN): ..."
```

**digitalmodel** (git plumbing — 4.2GB pack files):
```bash
# Preflight: verify staged files match expected set
git diff --cached --stat              # must show only intended files; abort if empty or unexpected
git symbolic-ref HEAD                 # verify not detached HEAD

TREE=$(git write-tree)
COMMIT=$(git commit-tree "$TREE" -p HEAD -m "refactor(wrk-NNN): ...")
git update-ref HEAD "$COMMIT"

# Post-commit verification
git show --name-status --stat -1      # verify correct files changed
git log -1 --format="%H %s"           # verify commit message
git diff HEAD~1 --name-only | sort    # compare to expected file list
```

### Rollback (if tests fail after shim creation)

**worldenergydata:**
```bash
# If not committed yet
git checkout -- safety_analysis/taxonomy/activity_taxonomy.py
git clean -f src/worldenergydata/safety_analysis/taxonomy/activity_definitions.py
git clean -f src/worldenergydata/safety_analysis/taxonomy/activity_registry.py
# If committed: git reset --hard <GOOD_HASH>
```

**digitalmodel:**
```bash
# If committed via plumbing
GOOD_HASH=$(git log --oneline | awk 'NR==2{print $1}')
git update-ref refs/heads/$(git symbolic-ref --short HEAD) "$GOOD_HASH"
git read-tree "$GOOD_HASH"
git checkout-index -a -f
# Then update hub submodule pointer: cd workspace-hub && git submodule update --init digitalmodel
```

---

## Critical Files

| File | Action |
|------|--------|
| `worldenergydata/src/worldenergydata/safety_analysis/taxonomy/activity_taxonomy.py` | Split → 2 modules + shim |
| `worldenergydata/src/worldenergydata/safety_analysis/taxonomy/activity_definitions.py` | NEW: models + 19 builders |
| `worldenergydata/src/worldenergydata/safety_analysis/taxonomy/activity_registry.py` | NEW: `ActivityTaxonomy` + query API |
| `worldenergydata/src/worldenergydata/safety_analysis/taxonomy/__init__.py` | Update imports |
| `worldenergydata/tests/safety_analysis/taxonomy/` | Verify green before/after |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_generator.py` | Split → 4 modules + shim |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_data_models.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_extractors.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_computations.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_builders.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_plotter.py` | Split → 4 modules + orchestrator |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_helpers.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_input_reports.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_rao_plots.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/benchmark_correlation.py` | NEW |
| `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/__init__.py` | Update imports |
| `digitalmodel/tests/hydrodynamics/diffraction/test_report_generator.py` | Verify green before/after |
| `digitalmodel/tests/hydrodynamics/diffraction/test_benchmark_plotter.py` | Verify green before/after |

---

## Planning Process Record

| Phase | Agent(s) | Output |
|-------|---------|--------|
| Phase 1 — Explore | 2 parallel Explore agents (different domains) | Detailed analysis of 5 candidates; 2 skipped (data file + already modular); 3 confirmed God Objects |
| Phase 2 — Design | 2 parallel Plan agents (risk + implementation) | 6 plan gaps identified and resolved; exact file headers, import blocks, creation order, rollback |
| Phase 3 — Cross-review | Codex (Claude + Gemini timed out) | REQUEST_CHANGES → all P1/P2/P3 items addressed |

## Cross-Review Status

| Reviewer | Status | Verdict |
|---------|--------|---------|
| Codex | ✓ Complete | REQUEST_CHANGES → addressed (Acceptance Criteria, Constants Policy, plumbing verification) |
| Claude | ✗ Timeout | |
| Gemini | ✗ Timeout | |
