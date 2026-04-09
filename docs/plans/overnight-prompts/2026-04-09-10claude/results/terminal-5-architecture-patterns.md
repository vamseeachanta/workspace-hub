# Terminal 5: Subsea Architecture Patterns — Dossier

## Issue Metadata

| Field | Value |
|---|---|
| Issue | [#2058](https://github.com/vamseeachanta/workspace-hub/issues/2058) |
| Title | feat(field-dev): subsea architecture patterns — flowline trends and layout classification |
| Labels | `enhancement`, `cat:engineering`, `agent:claude` |
| State | OPEN |
| Depends On | #1861 (scaffold — done, commit `aaf90c8e`) |
| Gate Status | **Needs `status:plan-approved`** before implementation can proceed |
| Generated | 2026-04-09 |

---

## 1. Current-State Findings

### 1.1 Files / Modules Already Present

| File | Lines | Role | Status |
|---|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | 241 | SubseaProject dataclass + benchmark aggregation functions | Scaffold complete (#1861) |
| `digitalmodel/tests/field_development/test_benchmarks.py` | 417 | TDD tests for existing benchmark functions | 25+ tests, all passing |
| `worldenergydata/subseaiq/analytics/normalize.py` | 130 | Raw SubseaIQ field alias mapping + type coercion | 10 canonical fields mapped |

### 1.2 What Exists in Detail

#### SubseaProject Dataclass (`benchmarks.py:53-70`)

Current 10 fields:

```
name: str                              # required
operator: Optional[str]
water_depth_m: Optional[float]
concept_type: Optional[str]            # e.g. "TLP", "Spar", "FPSO", "Subsea Tieback"
tieback_distance_km: Optional[float]
num_wells: Optional[int]
num_trees: Optional[int]
num_manifolds: Optional[int]
fluid_type: Optional[str]              # e.g. "oil", "gas"
region: Optional[str]
```

**Missing fields per #2058 scope:** `flowline_diameter_in`, `flowline_material`, `layout_type` — none present.

#### Existing Analytical Functions

1. **`load_projects(records)`** (`benchmarks.py:76-114`) — parses raw dicts into `SubseaProject` instances; raises `KeyError` if name missing.

2. **`concept_benchmark_bands(projects)`** (`benchmarks.py:121-149`) — returns `{depth_band: {concept_type: count}}` using 4 depth bands (`0-300m`, `300-800m`, `800-1500m`, `1500m+`). Filters out projects missing depth or concept type.

3. **`subsea_architecture_stats(projects)`** (`benchmarks.py:156-196`) — **global only** summary stats (count/min/max/mean) for:
   - `tieback_distance` — from `tieback_distance_km`
   - `trees_per_project` — from `num_trees`
   - `manifolds_per_project` — from `num_manifolds`
   - `trees_per_manifold` — computed ratio (excludes zero-manifold projects)

4. **Internal helpers:** `_classify_depth()` (line 203), `_describe()` (line 211), `_opt_float()` (line 223), `_opt_int()` (line 233).

#### Normalize Pipeline (`normalize.py:31-54`)

10 canonical fields with alias lists. **No aliases exist** for `flowline_diameter`, `flowline_material`, or `layout_type`. Functions: `normalize_project()` (line 57), `normalize_projects()` (line 94), plus `_first_match()`, `_safe_float()`, `_safe_int()`.

### 1.3 Tests Already Present

| Test Class | Tests | Coverage |
|---|---|---|
| `TestLoadProjects` (line 142) | 8 | Full: count, types, fields, sparse, missing name |
| `TestConceptBenchmarkBands` (line 186) | 8 | Full: all 4 bands, totals, missing depth, empty |
| `TestSubseaArchitectureStats` (line 258) | 6 | Full for **global** stats; no segmentation tests |
| `TestJunkValues` (line 317) | 3 | Robustness: N/A strings, string numbers, junk exclusion |
| `TestNormalizeIntegration` (line 359) | 1 | End-to-end: raw SubseaIQ keys through normalize + load + bands |

**Test fixture:** 8 synthetic projects (`FIXTURE_RECORDS`, lines 20-117) covering 6 concept types, 4 depth bands, 2 fluid types, 5 with tieback data. Plus 4 `SPARSE_RECORDS` (lines 120-125).

### 1.4 Latest Relevant Commits

| Commit | Description |
|---|---|
| `aaf90c8e` | #1861 scaffold — `SubseaProject`, `load_projects`, `concept_benchmark_bands`, `subsea_architecture_stats` |
| `d8a6fd841` | SubseaIQ scraping research strategy |
| `4d2423a4b` | Overnight exit report with next-phase issues (#1972-#1976) |

### 1.5 Related Modules (Read-Only Context)

- `digitalmodel/src/digitalmodel/field_development/concept_selection.py` — `HostType` enum, concept selection logic using depth/reservoir/distance/fluid.
- `digitalmodel/src/digitalmodel/field_development/subsea_bridge.py` — `GoMField` catalog (10 reference fields from `subseaiq-scan-latest.json`), separate from benchmark stats.
- `digitalmodel/src/digitalmodel/field_development/capex_estimator.py` — `estimate_capex()` uses tieback distance tiers.
- `data/field-development/subseaiq-scan-latest.json` — 10 GoM reference fields (Perdido, Appomattox, Whale, etc.) used by subsea_bridge, not benchmarks.

---

## 2. Remaining Implementation Delta

### 2.1 Exact Missing Behaviors

#### A. SubseaProject Fields (3 new fields)

`benchmarks.py:53-70` — Add after `region` (line 69):

```python
flowline_diameter_in: Optional[float] = None    # nominal pipe OD in inches
flowline_material: Optional[str] = None          # e.g. "Carbon Steel", "Duplex", "Flexible"
layout_type: Optional[str] = None                # e.g. "daisy_chain", "star", "direct_tieback"
```

`load_projects()` must also map these 3 new fields from the input dict (lines 100-113).

#### B. Normalize Aliases (3 new alias groups)

`normalize.py:31-54` — Add 3 new entries to `_FIELD_ALIASES`:

```python
"flowline_diameter_in": [
    "flowline_diameter_in", "Flowline Diameter (in)", "flowline_diameter",
    "pipe_diameter_in", "Pipe Diameter", "flowline_od_in",
],
"flowline_material": [
    "flowline_material", "Flowline Material", "pipe_material",
    "Pipeline Material", "material", "Material",
],
"layout_type": [
    "layout_type", "Layout Type", "layout", "Layout",
    "subsea_layout", "Subsea Layout", "architecture_type",
],
```

`normalize_project()` (line 57) needs coercion logic for `flowline_diameter_in` (float) and passthrough for the two string fields.

#### C. Layout Classification Function (NEW)

A new function `layout_distribution(projects) -> dict[str, dict[str, int]]` that returns `{concept_type: {layout_type: count}}`. Must handle None layout_type gracefully. Expected layout values: `"daisy_chain"`, `"star"`, `"direct_tieback"`, `"hub_spoke"`, etc.

#### D. Segmented Tieback Distance Stats (NEW)

A new function `tieback_stats_segmented(projects) -> dict[str, dict[str, dict[str, float]]]` returning `{depth_band: {fluid_type: {count, min, max, mean}}}`. Reuses existing `_classify_depth()` and `_describe()` helpers.

#### E. Segmented Equipment Count Stats (NEW)

A new function `equipment_stats_by_concept(projects) -> dict[str, dict[str, dict[str, float]]]` returning `{concept_type: {"trees_per_manifold": {stats}, "manifolds_per_host": {stats}}}`. Groups trees/manifold and manifolds/host by concept_type.

#### F. Flowline Trends by Depth (NEW)

A new function `flowline_trends_by_depth(projects) -> dict[str, dict[str, Any]]` returning `{depth_band: {"diameter": {stats}, "materials": {material: count}}}`. Requires the new `flowline_diameter_in` and `flowline_material` fields.

### 2.2 Exact File Paths That Must Change

| File | Change Type | Scope |
|---|---|---|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Extend | 3 new dataclass fields + 4 new public functions + update `load_projects` |
| `digitalmodel/tests/field_development/test_benchmarks.py` | Extend | ~15-20 new test methods across 4 new test classes |
| `worldenergydata/subseaiq/analytics/normalize.py` | Extend | 3 new alias groups + coercion for `flowline_diameter_in` |

---

## 3. TDD-First Execution Plan

### Phase 1: Failing Tests First

#### Step 1.1 — Test SubseaProject new fields

Add to `test_benchmarks.py`:

```python
class TestSubseaProjectNewFields:
    def test_flowline_diameter_loaded(self):
        # fixture record with flowline_diameter_in=10.75
        ...
    def test_flowline_material_loaded(self):
        # fixture record with flowline_material="Duplex"
        ...
    def test_layout_type_loaded(self):
        # fixture record with layout_type="daisy_chain"
        ...
    def test_new_fields_default_to_none(self):
        # existing sparse records still work, new fields are None
        ...
```

#### Step 1.2 — Test layout distribution

```python
class TestLayoutDistribution:
    def test_returns_dict_keyed_by_concept(self, projects):
        ...
    def test_counts_layout_types_per_concept(self, projects):
        ...
    def test_skips_none_layout(self, sparse_projects):
        ...
    def test_empty_input(self):
        ...
```

#### Step 1.3 — Test segmented tieback stats

```python
class TestTiebackStatsSegmented:
    def test_returns_nested_dict(self, projects):
        ...
    def test_segments_by_depth_band(self, projects):
        ...
    def test_segments_by_fluid_type(self, projects):
        ...
    def test_skips_missing_tieback(self, projects):
        ...
    def test_empty_input(self):
        ...
```

#### Step 1.4 — Test segmented equipment stats

```python
class TestEquipmentStatsByConcept:
    def test_returns_dict_keyed_by_concept(self, projects):
        ...
    def test_trees_per_manifold_by_concept(self, projects):
        ...
    def test_skips_zero_manifolds(self, projects):
        ...
    def test_empty_input(self):
        ...
```

#### Step 1.5 — Test flowline trends by depth

```python
class TestFlowlineTrendsByDepth:
    def test_diameter_stats_per_band(self, projects):
        ...
    def test_material_distribution_per_band(self, projects):
        ...
    def test_skips_none_flowline_fields(self, sparse_projects):
        ...
    def test_empty_input(self):
        ...
```

#### Step 1.6 — Test normalize aliases

```python
# In TestNormalizeIntegration or new class:
def test_flowline_diameter_alias(self):
    raw = [{"Project Name": "X", "Flowline Diameter (in)": 10.75}]
    normalized = normalize_projects(raw)
    assert normalized[0]["flowline_diameter_in"] == 10.75

def test_flowline_material_alias(self):
    raw = [{"Project Name": "X", "Pipeline Material": "Duplex"}]
    normalized = normalize_projects(raw)
    assert normalized[0]["flowline_material"] == "Duplex"

def test_layout_type_alias(self):
    raw = [{"Project Name": "X", "Layout Type": "star"}]
    normalized = normalize_projects(raw)
    assert normalized[0]["layout_type"] == "star"
```

### Phase 2: Implementation Steps

| Step | File | Change |
|---|---|---|
| 2.1 | `normalize.py` | Add 3 alias groups to `_FIELD_ALIASES` dict + float coercion for `flowline_diameter_in` |
| 2.2 | `benchmarks.py` | Add 3 fields to `SubseaProject` dataclass |
| 2.3 | `benchmarks.py` | Update `load_projects()` to map new fields |
| 2.4 | `benchmarks.py` | Implement `layout_distribution()` |
| 2.5 | `benchmarks.py` | Implement `tieback_stats_segmented()` |
| 2.6 | `benchmarks.py` | Implement `equipment_stats_by_concept()` |
| 2.7 | `benchmarks.py` | Implement `flowline_trends_by_depth()` |
| 2.8 | `test_benchmarks.py` | Extend `FIXTURE_RECORDS` with flowline/layout data for 3-4 projects |
| 2.9 | `test_benchmarks.py` | Run all tests, verify green |

### Phase 3: Verification Commands

```bash
# 1. Run all benchmark tests
cd /mnt/local-analysis/workspace-hub && uv run pytest digitalmodel/tests/field_development/test_benchmarks.py -v

# 2. Run normalize integration specifically
cd /mnt/local-analysis/workspace-hub && uv run pytest digitalmodel/tests/field_development/test_benchmarks.py::TestNormalizeIntegration -v

# 3. Type check (if mypy configured)
cd /mnt/local-analysis/workspace-hub && uv run python -c "from digitalmodel.field_development.benchmarks import SubseaProject; p = SubseaProject(name='test'); print(f'Fields: {[f.name for f in __import__(\"dataclasses\").fields(p)]}')"

# 4. Verify new fields exist on SubseaProject
cd /mnt/local-analysis/workspace-hub && uv run python -c "
from digitalmodel.field_development.benchmarks import SubseaProject
import dataclasses
fields = {f.name for f in dataclasses.fields(SubseaProject)}
required = {'flowline_diameter_in', 'flowline_material', 'layout_type'}
missing = required - fields
print(f'Missing fields: {missing}' if missing else 'All new fields present')
"

# 5. Verify new functions are importable
cd /mnt/local-analysis/workspace-hub && uv run python -c "
from digitalmodel.field_development.benchmarks import (
    layout_distribution,
    tieback_stats_segmented,
    equipment_stats_by_concept,
    flowline_trends_by_depth,
)
print('All new functions importable')
"

# 6. Verify normalize aliases exist
cd /mnt/local-analysis/workspace-hub && uv run python -c "
import sys; sys.path.insert(0, 'worldenergydata')
from subseaiq.analytics.normalize import _FIELD_ALIASES
required = {'flowline_diameter_in', 'flowline_material', 'layout_type'}
missing = required - set(_FIELD_ALIASES.keys())
print(f'Missing aliases: {missing}' if missing else 'All new aliases present')
"

# 7. Full regression (all field_development tests)
cd /mnt/local-analysis/workspace-hub && uv run pytest digitalmodel/tests/field_development/ -v --tb=short
```

---

## 4. Risk / Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Status | Resolution |
|---|---|---|
| Issue #2058 needs `status:plan-approved` label | **BLOCKING** | User must review this dossier and add the label |
| Depends on #1861 scaffold | **CLEAR** | Scaffold commit `aaf90c8e` already merged; `SubseaProject`, `load_projects`, `concept_benchmark_bands`, `subsea_architecture_stats` all present |

### 4.2 Data / Source Dependencies

| Dependency | Risk | Mitigation |
|---|---|---|
| SubseaIQ raw data may not include flowline diameter/material fields | **MEDIUM** | Verify actual SubseaIQ scrape output includes these fields before implementation. If not available, the new fields will exist on `SubseaProject` but remain None for most records |
| Layout type values are not standardized in SubseaIQ | **MEDIUM** | Implement a normalization function that maps common variants (e.g. "Daisy Chain", "daisy-chain") to canonical values (`daisy_chain`, `star`, `direct_tieback`, `hub_spoke`) |
| Test fixture data must be extended | **LOW** | Add flowline/layout fields to 3-4 of the 8 existing `FIXTURE_RECORDS` entries, keeping backward compatibility |

### 4.3 Merge / Contention Concerns

| Concern | Risk | Mitigation |
|---|---|---|
| `benchmarks.py` is a hot file (used by #1861, #1843, #2058) | **LOW** | All changes are additive (new fields, new functions); no existing lines modified except `load_projects()` field mapping |
| `normalize.py` shared between subsea analytics and benchmark pipeline | **LOW** | Only adding new entries to `_FIELD_ALIASES` dict and a coercion clause; existing fields untouched |
| `test_benchmarks.py` may have concurrent additions from parallel terminals | **LOW** | New test classes are self-contained; append-only changes minimize merge conflicts |
| Terminal 8 (subsea cost benchmarking) may touch overlapping files | **MEDIUM** | Coordinate: #2058 owns `subsea_architecture_stats` extension; cost benchmarking should use separate functions |

---

## 5. Ready-to-Execute Prompt

```
You are implementing GitHub issue #2058: feat(field-dev): subsea architecture patterns — flowline trends and layout classification.

## Context
The SubseaIQ benchmark bridge (`digitalmodel/src/digitalmodel/field_development/benchmarks.py`) already has `SubseaProject` dataclass (10 fields), `load_projects()`, `concept_benchmark_bands()`, and `subsea_architecture_stats()` (global stats only). The normalize pipeline (`worldenergydata/subseaiq/analytics/normalize.py`) maps 10 canonical fields from raw SubseaIQ data.

## What To Build (TDD — tests first)

### Step 1: Extend test fixtures
In `digitalmodel/tests/field_development/test_benchmarks.py`, add `flowline_diameter_in`, `flowline_material`, and `layout_type` to 4+ of the 8 `FIXTURE_RECORDS` entries (lines 20-117). Example values:
- Bravo: flowline_diameter_in=8.0, flowline_material="Carbon Steel", layout_type="direct_tieback"
- Delta: flowline_diameter_in=10.75, flowline_material="Duplex", layout_type="daisy_chain"
- Foxtrot: flowline_diameter_in=12.0, flowline_material="Flexible", layout_type="star"
- Golf: flowline_diameter_in=6.0, flowline_material="Carbon Steel", layout_type="direct_tieback"

### Step 2: Write failing tests
Add these test classes to `test_benchmarks.py`:
1. `TestSubseaProjectNewFields` — 4 tests: load each new field, defaults to None
2. `TestLayoutDistribution` — 4 tests: dict keyed by concept, counts per concept, skips None, empty
3. `TestTiebackStatsSegmented` — 5 tests: nested dict, by depth band, by fluid type, skips missing, empty
4. `TestEquipmentStatsByConcept` — 4 tests: by concept, trees/manifold per concept, skips zero, empty
5. `TestFlowlineTrendsByDepth` — 4 tests: diameter stats per band, material distribution, skips None, empty
6. `TestNormalizeNewFields` — 3 tests: each new alias variant resolves correctly

### Step 3: Implement
1. `worldenergydata/subseaiq/analytics/normalize.py` — add 3 alias groups to `_FIELD_ALIASES`, add float coercion for `flowline_diameter_in` in `normalize_project()`
2. `digitalmodel/src/digitalmodel/field_development/benchmarks.py`:
   - Add 3 fields to `SubseaProject` dataclass (after `region`, line 69)
   - Update `load_projects()` to map the 3 new fields
   - Add `layout_distribution(projects) -> dict[str, dict[str, int]]`
   - Add `tieback_stats_segmented(projects) -> dict[str, dict[str, dict[str, float]]]`
   - Add `equipment_stats_by_concept(projects) -> dict[str, dict[str, dict[str, float]]]`
   - Add `flowline_trends_by_depth(projects) -> dict[str, dict[str, Any]]`

### Step 4: Verify
```bash
uv run pytest digitalmodel/tests/field_development/test_benchmarks.py -v
uv run pytest digitalmodel/tests/field_development/ -v --tb=short
```

## Acceptance Criteria
- [ ] `SubseaProject` has `flowline_diameter_in`, `flowline_material`, `layout_type` fields
- [ ] `normalize.py` maps raw SubseaIQ variants for all 3 new fields
- [ ] `layout_distribution()` returns concept_type -> layout_type -> count
- [ ] `tieback_stats_segmented()` returns depth_band -> fluid_type -> {count, min, max, mean}
- [ ] `equipment_stats_by_concept()` returns concept_type -> metric -> {count, min, max, mean}
- [ ] `flowline_trends_by_depth()` returns depth_band -> {diameter stats, material counts}
- [ ] All existing tests still pass (zero regressions)
- [ ] All new tests pass
- [ ] No files exceed 500 lines (per worldenergydata CLAUDE.md constraint)

## Cross-Review Requirements
- Post `gh issue comment 2058 --body "..."` with implementation summary after completion
- Run `uv run pytest digitalmodel/tests/field_development/ -v` and include output
- Verify normalize integration test still passes end-to-end
```

---

## 6. Final Recommendation

**READY AFTER LABEL UPDATE**

All prerequisites are met:
- #1861 scaffold is merged and the 4 existing functions + 25 tests provide a solid foundation
- The implementation is purely additive — 3 new dataclass fields, 3 new normalize aliases, 4 new analytical functions
- No architectural decisions needed; the pattern is established by `subsea_architecture_stats()` and `_describe()`
- Risk is low: all changes are append-only with Optional fields defaulting to None

**Action required:** Add `status:plan-approved` label to issue #2058, then dispatch implementation agent with the prompt in Section 5.
