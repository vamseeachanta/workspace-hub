# Terminal 8 — Subsea Cost Benchmarking Dossier

## Issue Metadata

| Field              | Value                                                                   |
|--------------------|-------------------------------------------------------------------------|
| **Issue**          | #2055                                                                   |
| **Title**          | feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts|
| **Labels**         | enhancement, priority:high, cat:engineering, dark-intelligence, agent:claude |
| **Depends On**     | #1861 (scaffold — done)                                                 |
| **Status**         | NOT IMPLEMENTED — scaffold (#1861) complete, cost layer entirely absent  |
| **Dossier Date**   | 2026-04-09                                                              |

---

## 1. Current-State Findings

### 1.1 Files/Modules Already Present

| File | Status | What It Contains |
|------|--------|------------------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Exists (241 lines) | `SubseaProject` dataclass, `load_projects()`, `concept_benchmark_bands()`, `subsea_architecture_stats()`. **Zero cost functions.** |
| `digitalmodel/tests/field_development/test_benchmarks.py` | Exists (417 lines) | 4 test classes: `TestLoadProjects` (8 tests), `TestConceptBenchmarkBands` (8), `TestSubseaArchitectureStats` (7), `TestJunkValues` (3), `TestNormalizeIntegration` (1). **Zero cost-related tests.** |
| `digitalmodel/src/digitalmodel/field_development/capex_estimator.py` | Exists (227 lines) | `CAPEXEstimate`, `estimate_capex()`. Uses hardcoded GoM benchmarks (10 reference fields). Independent of SubseaIQ data. |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | Exists | Exports capex_estimator, concept_selection, opex_estimator, economics, schematic_generator. **Does NOT export benchmarks.** |
| `worldenergydata/subseaiq/analytics/normalize.py` | Exists (130 lines) | `normalize_project()`, `normalize_projects()`. Maps variant SubseaIQ keys to canonical schema (num_trees, num_manifolds, tieback_distance_km). Ready to consume. |
| `worldenergydata/subseaiq/analytics/__init__.py` | Exists | Empty — no public exports. |
| `worldenergydata/src/worldenergydata/cost/__init__.py` | Exists | Exports `CostDataPoint`, `load_public_dataset`, `CostPredictor`, `PredictionResult`. |
| `worldenergydata/src/worldenergydata/cost/data_collection/public_dataset.py` | Exists (1643 lines) | **71 sanctioned project cost records** as `CostDataPoint` Pydantic objects. Projects span GOM, NCS, Brazil, West Africa, etc. Costs in USD MM. |
| `worldenergydata/src/worldenergydata/cost/data_collection/calibration_schema.py` | Exists (157 lines) | `CostDataPoint` Pydantic schema. Has `project_name`, `region`, `water_depth_m`, `water_depth_band`, `cost_usd_mm`, `cost_type`, `subsea` type. **No equipment count fields (no num_trees, num_manifolds, tieback_distance_km, flowline_km).** |
| `worldenergydata/src/worldenergydata/cost/calibration/cost_predictor.py` | Exists | `CostPredictor` — sklearn LinearRegression on `CostDataPoint`. Features: water depth, region, rig type, year, HPHT, subsea. **No equipment count features.** |
| `digitalmodel/src/digitalmodel/field_development/subsea_bridge.py` | Exists (530 lines) | `SubseaFieldCatalog`, `GoMField`, `AnalogueMatch`. Loads from `data/field-development/subseaiq-scan-latest.json`. |
| `data/field-development/subseaiq-scan-latest.json` | Exists | 10 GoM reference fields. Schema: `{name, operator, water_depth_m, host, year, capacity_bopd}`. **No equipment counts.** |

### 1.2 Tests Already Present

All tests in `test_benchmarks.py` cover the #1861 scaffold only:
- `TestLoadProjects` — parsing records → `SubseaProject`
- `TestConceptBenchmarkBands` — depth-band aggregation of concept types
- `TestSubseaArchitectureStats` — min/max/mean for tieback, trees, manifolds
- `TestJunkValues` — robustness to scraped junk
- `TestNormalizeIntegration` — raw SubseaIQ keys → normalize → load pipeline

**No tests exist for cost correlation, cost curves, cost benchmarks, or cost per equipment.**

### 1.3 Relevant Commits

| Commit | Description |
|--------|-------------|
| `aaf90c8e` (referenced in issue) | Scaffold commit for #1861 — not found in local history (likely squashed or rebased) |
| `4d2423a4b` | Most recent benchmark-adjacent commit: overnight exit report + next-phase GH issues |
| `b6a4ca060` | Dark intelligence Excel assessment, field dev content map |

No commits reference #2055 or cost benchmarking against equipment counts.

---

## 2. Remaining Implementation Delta

### 2.1 Core Architectural Gap

The issue's central challenge is a **data correlation problem**:
- **Source A**: `SubseaProject` (benchmarks.py) has equipment counts (num_trees, num_manifolds, tieback_distance_km) but no costs.
- **Source B**: `CostDataPoint` (public_dataset.py) has 71 project costs (cost_usd_mm) but no equipment counts.
- **Join key**: `project_name` / `name` — but naming conventions differ and only ~10 GoM fields overlap.

The implementation must either:
1. **Extend CostDataPoint schema** with optional equipment count fields and backfill data for the 71 records, or
2. **Create a new CostCorrelation dataclass** that merges both schemas by project name match, or
3. **Use SubseaIQ equipment stats aggregated by water-depth band** to compute cost-per-equipment ratios at the band level (avoids per-project join).

**Recommendation**: Option 3 (band-level correlation) is most robust given sparse per-project equipment data. Option 1 is the stretch goal for higher fidelity.

### 2.2 Exact Missing Behaviors

| # | Missing Behavior | Target Location |
|---|-----------------|-----------------|
| 1 | `SubseaProject.cost_usd_mm` field (or separate join structure) | `benchmarks.py` line ~70 |
| 2 | `cost_per_tree(projects)` → dict by depth band | New function in `benchmarks.py` |
| 3 | `cost_per_km_flowline(projects)` → dict by depth band | New function in `benchmarks.py` |
| 4 | `cost_per_manifold(projects)` → dict by depth band | New function in `benchmarks.py` |
| 5 | `unit_cost_curves(projects)` → structured output of all 3 unit cost types | New function in `benchmarks.py` |
| 6 | `cost_benchmark_bands(projects)` → cost ranges by water depth + concept type | New function in `benchmarks.py` |
| 7 | Cross-validation against 71 sanctioned project costs | New function or integration in `benchmarks.py` |
| 8 | Cost correlation helper: merge SubseaIQ equipment data with cost data | New file `worldenergydata/subseaiq/analytics/cost_correlation.py` |
| 9 | Export benchmarks from `__init__.py` | `digitalmodel/src/digitalmodel/field_development/__init__.py` |

### 2.3 Exact File Paths That Should Change

| File | Change Type |
|------|-------------|
| `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | **EXTEND** — add cost fields to `SubseaProject`, add 5+ new cost functions |
| `digitalmodel/tests/field_development/test_benchmarks.py` | **EXTEND** — add cost-related test classes |
| `worldenergydata/subseaiq/analytics/cost_correlation.py` | **CREATE** — cost correlation helpers |
| `worldenergydata/subseaiq/analytics/__init__.py` | **EXTEND** — export cost correlation |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | **EXTEND** — export benchmarks |
| `data/field-development/subseaiq-scan-latest.json` | **EXTEND** — add equipment count fields to GoM records (or create new data file) |

---

## 3. TDD-First Execution Plan

### 3.1 Phase 1 — Failing Tests First

Add to `digitalmodel/tests/field_development/test_benchmarks.py`:

```python
# Test class 1: Cost fields on SubseaProject
class TestSubseaProjectCostFields:
    def test_cost_field_present(self):
        """SubseaProject should accept optional cost_usd_mm."""
    def test_cost_field_defaults_to_none(self):
        """cost_usd_mm should default to None when not provided."""

# Test class 2: Unit cost curves
class TestUnitCostCurves:
    def test_cost_per_tree_by_depth_band(self):
        """cost_per_tree() returns dict[depth_band -> float]."""
    def test_cost_per_tree_excludes_zero_trees(self):
        """Projects with 0 trees excluded from cost/tree calc."""
    def test_cost_per_km_flowline_by_depth_band(self):
        """cost_per_km_flowline() returns dict[depth_band -> float]."""
    def test_cost_per_manifold_by_depth_band(self):
        """cost_per_manifold() returns dict[depth_band -> float]."""
    def test_unit_cost_curves_structure(self):
        """unit_cost_curves() returns all 3 metrics keyed by depth band."""
    def test_sparse_data_handled(self):
        """Missing cost or equipment data → excluded, not crashed."""

# Test class 3: Cost benchmark bands
class TestCostBenchmarkBands:
    def test_returns_bands_by_depth_and_concept(self):
        """cost_benchmark_bands() returns nested dict[depth_band][concept_type] -> {low, base, high}."""
    def test_band_values_are_positive(self):
        """All cost band values should be > 0 where data exists."""
    def test_empty_bands_for_no_data(self):
        """Depth/concept combos with no data return empty or None."""

# Test class 4: Cross-validation against sanctioned projects
class TestCrossValidation:
    def test_cross_validate_returns_comparison(self):
        """cross_validate_costs() returns per-project comparison with delta."""
    def test_cross_validate_flags_outliers(self):
        """Projects where equipment-derived cost differs >50% from sanctioned cost flagged."""
```

### 3.2 Phase 2 — Implementation Steps

1. **Add `cost_usd_mm: Optional[float]` to `SubseaProject`** in `benchmarks.py:54-70`
2. **Update `load_projects()`** to parse `cost_usd_mm` field
3. **Create `worldenergydata/subseaiq/analytics/cost_correlation.py`**:
   - `correlate_equipment_costs(subseaiq_records, cost_records)` — name-match join
   - `aggregate_costs_by_depth_band(merged)` — band-level cost aggregation
4. **Add cost functions to `benchmarks.py`**:
   - `cost_per_tree(projects) -> dict[str, dict[str, float]]`
   - `cost_per_km_flowline(projects) -> dict[str, dict[str, float]]`
   - `cost_per_manifold(projects) -> dict[str, dict[str, float]]`
   - `unit_cost_curves(projects) -> dict[str, dict[str, dict[str, float]]]`
   - `cost_benchmark_bands(projects) -> dict[str, dict[str, dict[str, float]]]`
   - `cross_validate_costs(projects, sanctioned_costs) -> list[dict]`
5. **Update `__init__.py`** to export new benchmarks functions
6. **Backfill `subseaiq-scan-latest.json`** with equipment counts for 10 GoM fields (from public SubseaIQ data)

### 3.3 Verification Commands

```bash
# 1. Run existing benchmark tests (must still pass)
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v

# 2. Run new cost-related tests
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v -k "Cost"

# 3. Verify cost correlation helpers
cd worldenergydata && uv run pytest -v -k "cost_correlation"

# 4. Verify public_dataset still loads (71 records)
cd worldenergydata && uv run python -c "from worldenergydata.cost import load_public_dataset; d=load_public_dataset(); print(f'{len(d)} records loaded'); assert len(d) == 71"

# 5. Verify benchmarks import works
cd digitalmodel && uv run python -c "from digitalmodel.field_development.benchmarks import cost_per_tree, cost_benchmark_bands; print('imports OK')"

# 6. Verify normalize → benchmarks pipeline (integration)
cd digitalmodel && uv run pytest tests/field_development/test_benchmarks.py -v -k "Normalize"

# 7. Type check
cd digitalmodel && uv run mypy src/digitalmodel/field_development/benchmarks.py --ignore-missing-imports
```

---

## 4. Risk/Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| Issue #2055 not labeled `status:plan-approved` | **BLOCKING** — AGENTS.md requires approval before implementation | Add label after user reviews this dossier |
| benchmarks.py not exported from `__init__.py` | Low — easy fix but downstream consumers may not discover it | Include in implementation scope |

### 4.2 Data/Source Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| `worldenergydata.cost.data_collection.public_dataset` (71 records) | **AVAILABLE** — 71 `CostDataPoint` records with `cost_usd_mm` | LOW — data exists |
| SubseaIQ equipment count data | **PARTIAL** — `normalize.py` can parse them, `SubseaProject` can hold them, but `subseaiq-scan-latest.json` has **NO equipment counts** (only name, operator, depth, host, year, capacity) | **HIGH** — must either backfill JSON or source equipment counts separately |
| `CostDataPoint` schema lacks equipment fields | **GAP** — no `num_trees`, `num_manifolds`, `tieback_distance_km` on the 71 cost records | **MEDIUM** — can work around with band-level aggregation, but per-project correlation requires schema extension or separate join table |
| Cross-repo import path (digitalmodel importing from worldenergydata) | **WORKS** — `TestNormalizeIntegration` already does this via `sys.path.insert` | LOW — pattern established |

### 4.3 Likely Merge/Contention Concerns

| File | Contention Risk | Notes |
|------|----------------|-------|
| `benchmarks.py` | MEDIUM | Terminal 3 (timeline benchmarks) may also touch this file |
| `__init__.py` | LOW | Simple additive export |
| `test_benchmarks.py` | LOW | Additive test classes, append-only |
| `subseaiq-scan-latest.json` | MEDIUM | Overnight research may regenerate this file |
| `worldenergydata/subseaiq/analytics/` | LOW | New file creation, no existing code to conflict |

---

## 5. Ready-to-Execute Prompt

```
You are implementing GitHub issue #2055: feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts.

## Context
- Workspace: /mnt/local-analysis/workspace-hub
- Issue depends on #1861 (scaffold — DONE)
- Read the dossier at docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md for full current-state analysis

## What Already Exists
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` — SubseaProject dataclass, load_projects, concept_benchmark_bands, subsea_architecture_stats (no cost functions)
- `digitalmodel/tests/field_development/test_benchmarks.py` — 27 tests for #1861 scaffold (no cost tests)
- `worldenergydata/src/worldenergydata/cost/data_collection/public_dataset.py` — 71 sanctioned project cost records (CostDataPoint with cost_usd_mm)
- `worldenergydata/subseaiq/analytics/normalize.py` — normalizes raw SubseaIQ keys including equipment counts
- `data/field-development/subseaiq-scan-latest.json` — 10 GoM fields WITHOUT equipment count data

## TDD Implementation Order
1. ADD failing tests to `digitalmodel/tests/field_development/test_benchmarks.py` for:
   - SubseaProject.cost_usd_mm optional field
   - cost_per_tree(projects) -> dict by depth band
   - cost_per_km_flowline(projects) -> dict by depth band
   - cost_per_manifold(projects) -> dict by depth band
   - unit_cost_curves(projects) -> combined output
   - cost_benchmark_bands(projects) -> cost ranges by depth + concept type
   - cross_validate_costs(projects, sanctioned) -> comparison list
2. IMPLEMENT cost functions in benchmarks.py
3. CREATE worldenergydata/subseaiq/analytics/cost_correlation.py with correlation helpers
4. EXTEND subseaiq-scan-latest.json with equipment count fields for 10 GoM fields
5. UPDATE digitalmodel/src/digitalmodel/field_development/__init__.py to export benchmarks

## Acceptance Criteria
- [ ] `uv run pytest tests/field_development/test_benchmarks.py -v` — all pass including new cost tests
- [ ] cost_per_tree returns dict keyed by DEPTH_BANDS with float values
- [ ] cost_per_km_flowline returns dict keyed by DEPTH_BANDS with float values
- [ ] cost_per_manifold returns dict keyed by DEPTH_BANDS with float values
- [ ] cost_benchmark_bands returns nested dict[depth_band][concept_type] → {low, base, high}
- [ ] cross_validate_costs compares equipment-derived costs against 71 sanctioned records
- [ ] No regressions in existing 27 test_benchmarks.py tests
- [ ] `from digitalmodel.field_development.benchmarks import cost_per_tree` works

## Cross-Review Requirements
- Codex or Gemini cross-review before merge
- Verify cost curves produce physically reasonable values (cost/tree $10-200M range, cost/km $5-50M range)
- Verify no hardcoded absolute paths
- Verify existing test_benchmarks tests still pass unchanged
```

---

## 6. Final Recommendation

### **NEEDS ISSUE REFINEMENT**

**Rationale**: The issue assumes SubseaIQ equipment count data is available for correlation, but:

1. **`subseaiq-scan-latest.json`** (the actual data file) has **zero equipment count fields** — only name, operator, water_depth_m, host, year, capacity_bopd. The `normalize.py` aliases and `SubseaProject` dataclass are ready to consume equipment counts, but the data itself is missing.

2. **`CostDataPoint` schema** (the 71 sanctioned project records) has **no equipment count fields** — so per-project cost-per-tree correlation requires either schema extension or a separate mapping table.

3. The issue says "Depends on SubseaIQ scraping with equipment count fields" — this dependency is **NOT MET**. The scraping infrastructure (normalize.py) exists but has never produced data with trees/manifolds/tieback fields populated.

**Before labeling `status:plan-approved`**, resolve:
- [ ] Confirm that SubseaIQ equipment count scraping has actually populated data, OR scope the issue to use synthetic/manual equipment counts for the 10 GoM reference fields
- [ ] Decide correlation architecture: band-level aggregation (feasible now) vs per-project join (needs schema work)
- [ ] Clarify whether `CostDataPoint` schema should be extended with equipment fields, or whether a separate join table is preferred

**If the user is willing to manually backfill equipment counts for the 10 GoM fields in the JSON**, this issue can proceed immediately as a `READY AFTER LABEL UPDATE` with band-level correlation as the initial implementation.
