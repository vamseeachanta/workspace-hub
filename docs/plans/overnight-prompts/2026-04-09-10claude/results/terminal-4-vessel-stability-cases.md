# Terminal 4 — Real Vessel Stability Test Cases from Fleet Data

## Issue Metadata
| Field | Value |
|-------|-------|
| Issue | #2059 |
| Title | feat(naval-arch): real vessel stability test cases from fleet data (Sleipnir, Thialf, Balder) |
| Labels | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| Depends On | #1859 (vessel fleet adapter) -- DONE, #1850 (floating platform stability) -- DONE |
| Date | 2026-04-09 |
| Status | PARTIALLY IMPLEMENTED -- see delta below |

---

## 1. Current-State Findings

### 1.1 Source Modules Already Present

| File | Lines | Status | Key Functions |
|------|-------|--------|---------------|
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | 309 | COMPLETE | `register_fleet_vessels()`, `normalize_fleet_record()`, `estimate_vessel_hydrostatics()`, `get_ship()`, `list_ships()` |
| `digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py` | 331 | COMPLETE | `compute_gm()`, `compute_gz_curve()`, `compute_area_under_gz()`, `compute_wind_heel()`, `check_intact_stability()`, `PlatformType.SEMISUB`, `STABILITY_CRITERIA` |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py` | 205 | COMPLETE | `validate_vessel_entry()`, `merge_template_into_registry()` |
| `digitalmodel/src/digitalmodel/naval_architecture/curves_of_form.py` | 56 | COMPLETE | `displacement_at_draft()` -- bridges fleet vessels into hydrostatics |
| `digitalmodel/src/digitalmodel/naval_architecture/hydrostatics.py` | 81 | COMPLETE | `submerged_volume()`, `buoyant_force()` |

### 1.2 Data Sources

| File | Records | Notes |
|------|---------|-------|
| `worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv` | 17 vessels | 7 semi-submersibles, 9 monohulls, 1 jack-up |

**Semi-submersible vessels in CSV (the stability-relevant set):**

| Vessel | LOA (m) | Beam (m) | Draft (m) | Displacement (t) | Owner | Year |
|--------|---------|----------|-----------|-------------------|-------|------|
| SLEIPNIR | 220.0 | 102.0 | 27.5 | -- (missing) | Heerema | 2019 |
| THIALF | 201.0 | 88.4 | 31.2 | 71,368 | Heerema | 1985 |
| BALDER | 152.0 | 76.8 | 25.0 | -- (missing) | Heerema | 1978 |
| SAIPEM 7000 | 198.0 | 87.0 | 25.0 | -- (missing) | Saipem | -- |
| SAIPEM FDS | 152.0 | 92.0 | 23.0 | -- (missing) | Saipem | -- |
| SAIPEM FDS2 | 152.0 | 92.0 | 23.0 | -- (missing) | Saipem | -- |
| DLV 2000 | 170.0 | 54.0 | 18.0 | -- (missing) | McDermott | -- |

### 1.3 Tests Already Present

| File | Lines | Test Classes | Coverage |
|------|-------|-------------|----------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | 399 | 6 classes, ~20 tests | Partial -- see gaps below |
| `digitalmodel/tests/naval_architecture/test_floating_platform_stability.py` | 249 | 5 classes | Complete for generic platforms |

**Existing test fixtures in `test_vessel_fleet_adapter.py`:**
- `SLEIPNIR_RECORD` (lines 15-29) -- 220m x 102m x 27.5m, no displacement
- `THIALF_RECORD` (lines 31-45) -- 201m x 88.4m x 31.2m, 71,368 tonnes

**Existing test classes and what they cover:**
1. `TestNormalizeFleetRecord` (lines 63-123) -- unit conversion, partial records, metadata
2. `TestRegisterFleetVessels` (lines 125-186) -- batch registration, duplicates, overwrite
3. `TestStabilityIntegration` (lines 188-247) -- submerged volume (THIALF), BM estimate (SLEIPNIR), list check
4. `TestNormalizeDrillingRigRecord` (lines 267-306) -- drilling rig normalization
5. `TestEstimateVesselHydrostatics` (lines 308-342) -- CB/KB/BM/KG estimation
6. `TestFloatingPlatformStabilityIntegration` (lines 365-398) -- THIALF-only end-to-end stability

### 1.4 Current Test Run Results (2026-04-09)

```
28 passed, 1 failed in 38.92s
```

**Pre-existing failure**: `TestRegisterFleetVessels::test_register_multiple_vessels` (line 136) fails with `assert 0 >= 1` due to test-ordering dependency. The `_SHIPS` registry is module-level mutable state; earlier tests register the same vessels, so re-registration returns `added=0`. This is a pre-existing isolation bug, not caused by missing implementation.

### 1.5 Latest Relevant Commits

The commits `81da910a` and `197fc901` referenced in issue #2059 body are from issue #1859 and implemented `register_fleet_vessels()`. The functionality is present in the current codebase (verified via source inspection).

---

## 2. Remaining Implementation Delta

### 2.1 Missing Behaviors (5 gaps)

**Gap 1: BALDER vessel fixture and registration test**
- The CSV contains BALDER (152m x 76.8m x 25m, Heerema, 1978, DP2, 6300t crane)
- No `BALDER_RECORD` fixture exists in `test_vessel_fleet_adapter.py`
- No tests register or exercise Balder at all
- Priority: HIGH -- issue title explicitly names Balder

**Gap 2: Full stability pipeline for all 3 named semi-subs**
- Only THIALF has a `check_intact_stability()` test (`test_thialf_stability_check_runs`, line 366)
- SLEIPNIR has a BM estimate test but no GZ curve or IMO criteria check
- BALDER has no tests at all
- Required: All 3 vessels produce non-trivial `StabilityResult` with GZ curves
- Priority: HIGH -- acceptance criterion AC-1

**Gap 3: CSV-based bulk registration fixture**
- Tests use hardcoded dict fixtures, not the actual CSV
- Issue asks: "Register all 17 construction vessels from `construction_vessels.csv` via `register_fleet_vessels()` in a test fixture"
- Required: A test that loads the CSV, calls `register_fleet_vessels()`, and verifies count
- Priority: MEDIUM -- issue AC says "at least 3 real construction vessels produce non-trivial stability results"

**Gap 4: Physical reasonableness validation of GZ curves**
- Existing THIALF test only checks `result.gm_m > 0` and `isinstance(result.intact, bool)`
- Does NOT validate:
  - GZ curve has positive initial slope (stable)
  - Max GZ occurs at a physically reasonable heel angle (20-60 deg)
  - Area criteria have numerically reasonable values
  - GM values are within expected range for semi-submersible vessels
- Required: Tests that assert physically meaningful stability metrics
- Priority: HIGH -- acceptance criterion AC-3

**Gap 5: Assumed vs measured parameter documentation**
- Tests do not document which values are assumed and which are measured
- Key parameters in `estimate_vessel_hydrostatics()` use defaults:
  - `KB = 0.53 * draft` (assumption -- box approximation is KB = T/2 = 0.50*T)
  - `Cb = 0.65` default (assumption -- inappropriate for semi-subs, which typically have Cb = 0.40-0.55)
  - `Cw = 0.72` default (assumption -- may be too high for semi-sub twin-hull waterplanes)
  - `KG = 0.6 * draft` default (assumption -- varies significantly by loading condition)
- Only THIALF has measured displacement (71,368 t); Sleipnir and Balder have no displacement data
- Required: Test docstrings and/or parametrize IDs clearly marking "assumed" vs "measured"
- Priority: MEDIUM -- acceptance criterion AC-3

### 2.2 Technical Concern: Semi-Sub Form Coefficients

The `estimate_vessel_hydrostatics()` function uses monohull defaults:
- `Cb_default = 0.65` -- conventional ships range 0.50-0.85; semi-subs are typically 0.40-0.55 due to twin pontoon/column geometry
- `Cw_default = 0.72` -- semi-sub waterplane is dominated by columns (small waterplane area relative to LOA*BEAM)
- BM formula `Iwp/V` with `Iwp = Cw * L * B^3 / 12` overestimates BM for semi-subs because waterplane is not a simple rectangle

This means stability estimates for semi-subs will be approximate. The issue acknowledges this by requesting "estimated values or parametric formulas." Tests should clearly document the approximation and bound the expected error range.

### 2.3 Files That Should Change

| File | Action | Reason |
|------|--------|--------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | EXTEND | Add BALDER_RECORD fixture, CSV-load test, per-vessel stability tests, reasonableness assertions |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | POSSIBLE MINOR EDIT | May need semi-sub-specific Cb/Cw defaults in `estimate_vessel_hydrostatics()` |
| `digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py` | NO CHANGE EXPECTED | Already complete |

---

## 3. TDD-First Execution Plan

### Phase 1: Failing Tests (write first)

**Step 1.1 -- Add BALDER_RECORD fixture**
```python
BALDER_RECORD = {
    "VESSEL_NAME": "BALDER",
    "VESSEL_CATEGORY": "construction",
    "VESSEL_TYPE": "crane_vessel",
    "VESSEL_SUBTYPE": "semi_submersible",
    "OWNER": "Heerema Marine Contractors",
    "LOA_M": 152.0,
    "BEAM_M": 76.8,
    "DRAFT_M": 25.0,
    "DISPLACEMENT_TONNES": None,
    "GROSS_TONNAGE": None,
    "DP_CLASS": 2,
    "YEAR_BUILT": 1978,
    "MAIN_CRANE_CAPACITY_T": 6300.0,
}
```

**Step 1.2 -- Add CSV-based bulk registration test**
```python
class TestCSVBulkRegistration:
    def test_register_all_17_from_csv(self):
        """Load all 17 construction vessels from worldenergydata CSV."""
        import csv, pathlib
        csv_path = pathlib.Path(__file__).resolve().parents[3] / (
            "worldenergydata/data/modules/vessel_fleet/"
            "curated/construction_vessels.csv"
        )
        with open(csv_path) as f:
            records = list(csv.DictReader(f))
        added, skipped = register_fleet_vessels(records)
        assert added + skipped == 17
        assert added >= 15  # most should register
```

**Step 1.3 -- Add parametrized stability test for 3 named semi-subs**
```python
@pytest.mark.parametrize("record,vessel_name", [
    (SLEIPNIR_RECORD, "SLEIPNIR"),
    (THIALF_RECORD, "THIALF"),
    (BALDER_RECORD, "BALDER"),
], ids=["sleipnir-assumed-Cb", "thialf-measured-disp", "balder-assumed-Cb"])
class TestRealVesselStability:
    def test_stability_produces_nontrivial_result(self, record, vessel_name):
        """AC-1: at least 3 real vessels produce non-trivial stability results."""
        ...  # register, estimate hydrostatics, compute_gz_curve, check_intact_stability

    def test_gz_curve_physically_reasonable(self, record, vessel_name):
        """AC-2: GZ curves produce physically reasonable shapes."""
        ...  # positive GZ at small angles, peak between 20-60 deg, declining after peak

    def test_semisub_imo_criteria_evaluation(self, record, vessel_name):
        """AC-2: Semi-subs pass/fail IMO criteria as expected."""
        ...  # check against SEMISUB criteria (min_gm=1.0m)

    def test_assumed_vs_measured_clearly_labeled(self, record, vessel_name):
        """AC-3: Tests document assumed vs measured parameters."""
        ...  # verify parameter sourcing is documented
```

**Step 1.4 -- Add GZ curve shape validation test**
```python
def test_gz_curve_initial_positive_slope(self):
    """GZ must increase from 0 at 0 deg -- confirms positive GM."""

def test_area_under_gz_reasonable_range(self):
    """Area 0-30 for semi-sub with GM > 1m should be in 0.01-0.5 m-rad."""
```

### Phase 2: Implementation Steps

**Step 2.1** -- Add BALDER_RECORD to test_vessel_fleet_adapter.py after THIALF_RECORD (line 45)

**Step 2.2** -- (Optional) Enhance `estimate_vessel_hydrostatics()` to accept vessel_subtype parameter and use semi-sub-specific defaults:
- If vessel_subtype == "semi_submersible": Cb_default = 0.50, Cw_default = 0.55
- This improves physical accuracy without breaking existing tests

**Step 2.3** -- Implement the failing test bodies:
- Register vessel, get hydrostatics, compute GZ curve via wall-sided formula
- Validate StabilityResult fields against expected ranges
- Document in test IDs/docstrings which parameters are assumed

**Step 2.4** -- Add the CSV-loading test with proper path resolution

### Phase 3: Verification

```bash
# Run only the fleet adapter tests
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short

# Run full naval architecture test suite
cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short

# Run stability-specific tests
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_floating_platform_stability.py -v --tb=short

# Spot-check: Balder stability estimate (quick Python REPL sanity check)
cd digitalmodel && uv run python -c "
from digitalmodel.naval_architecture.ship_data import register_fleet_vessels, get_ship, estimate_vessel_hydrostatics
from digitalmodel.naval_architecture.floating_platform_stability import compute_gz_curve, compute_wind_heel, check_intact_stability
BALDER = {'VESSEL_NAME': 'BALDER', 'LOA_M': 152.0, 'BEAM_M': 76.8, 'DRAFT_M': 25.0}
register_fleet_vessels([BALDER])
ship = get_ship('BALDER')
h = estimate_vessel_hydrostatics(ship)
print(f'GM={h[\"gm_ft\"]:.1f} ft, BM={h[\"bm_ft\"]:.1f} ft, KB={h[\"kb_ft\"]:.1f} ft, KG={h[\"kg_ft\"]:.1f} ft')
gm_m = h['gm_ft'] * 0.3048
print(f'GM={gm_m:.2f} m (SEMISUB min: 1.0 m)')
gz = compute_gz_curve(gm_m)
print(f'GZ curve: {len(gz)} points, max GZ={max(g for _, g in gz):.3f} m at {gz[[g for _, g in gz].index(max(g for _, g in gz))][0]:.0f} deg')
"

# Verify CSV path resolves from test file location
cd digitalmodel && uv run python -c "
import pathlib
csv_path = pathlib.Path('tests/naval_architecture/test_vessel_fleet_adapter.py').resolve().parents[3] / 'worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv'
print(f'CSV exists: {csv_path.exists()}, records: {sum(1 for _ in open(csv_path)) - 1}')
"
```

---

## 4. Risk / Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| Issue #2059 is NOT labeled `status:plan-approved` | BLOCKING | Must add label before implementation begins per AGENTS.md |
| No existing `status:plan-review` label on issue | BLOCKING | This dossier should be attached to the issue and labeled `status:plan-review` |

### 4.2 Data/Source Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| `worldenergydata` submodule must be checked out | OK -- CSV exists at expected path | Low -- submodule is tracked |
| Sleipnir displacement is MISSING from CSV | GAP | Medium -- tests must use estimated Cb (documented as assumed) |
| Balder displacement is MISSING from CSV | GAP | Medium -- same approach as Sleipnir |
| Only THIALF has measured displacement (71,368 t) | KNOWN | Low -- the issue anticipates this and asks for estimation formulas |
| Semi-sub Cb/Cw defaults (0.65/0.72) are monohull values | CONCERN | Medium -- may produce unrealistic GM values for semi-subs; tests should bound acceptable range rather than asserting exact values |

### 4.3 Merge/Contention Concerns

| Concern | Likelihood | Mitigation |
|---------|------------|------------|
| `test_vessel_fleet_adapter.py` concurrent edits | LOW | File is 399 lines, changes are additive (new fixtures + new test classes at end) |
| `ship_data.py` Cb/Cw enhancement | LOW | Optional enhancement; main work is test-only |
| `worldenergydata` submodule pinning | LOW | Read-only dependency; no changes to submodule |

---

## 5. Ready-to-Execute Prompt

```
TASK: Implement #2059 — real vessel stability test cases from fleet data

CONTEXT:
- Issue #2059 depends on #1859 (fleet adapter, DONE) and #1850 (stability, DONE)
- Source: `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`
- Source: `digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py`
- Tests: `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py`
- CSV: `worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv`

STEP 1 — ADD FIXTURES (TDD: write tests first):
1. Add BALDER_RECORD fixture after THIALF_RECORD (line 45) in test_vessel_fleet_adapter.py:
   - VESSEL_NAME: BALDER, LOA_M: 152.0, BEAM_M: 76.8, DRAFT_M: 25.0
   - VESSEL_CATEGORY: construction, VESSEL_TYPE: crane_vessel, VESSEL_SUBTYPE: semi_submersible
   - OWNER: Heerema Marine Contractors, YEAR_BUILT: 1978, DP_CLASS: 2
   - MAIN_CRANE_CAPACITY_T: 6300.0, DISPLACEMENT_TONNES: None

2. Add a TestCSVBulkRegistration class that:
   - Loads construction_vessels.csv (17 records) via csv.DictReader
   - Calls register_fleet_vessels(records)
   - Asserts added + skipped == 17 and added >= 15

STEP 2 — ADD PARAMETRIZED STABILITY TESTS:
3. Add @pytest.mark.parametrize test class TestRealVesselStability with IDs:
   - "sleipnir-assumed-Cb" — uses estimated displacement (Cb_default)
   - "thialf-measured-disp" — uses actual 71,368 tonne displacement
   - "balder-assumed-Cb" — uses estimated displacement (Cb_default)

4. Each vessel test should:
   a. register_fleet_vessels([record])
   b. get_ship(name) and estimate_vessel_hydrostatics(ship)
   c. Convert GM to meters: gm_m = hydro["gm_ft"] * 0.3048
   d. compute_gz_curve(gm_m) with default heel angles (0-90 by 5)
   e. compute_wind_heel(wind_pressure_kpa=0.5, projected_area_m2=5000, heeling_arm_m=15.0, displacement_t=est_disp, gm_m=gm_m)
   f. check_intact_stability("semisubmersible", gm_m, gz_curve, wind)
   g. Assert: gm_m > 0, len(gz_curve) >= 10, max_gz > 0, result has intact bool

5. Physical reasonableness assertions:
   - GM should be between 0.5 and 50 meters for these large semi-subs
   - Max GZ should occur between 15 and 70 degrees
   - GZ at 30 degrees should be positive
   - Area 0-30 should be positive

6. Add docstrings to every test documenting which parameters are ASSUMED vs MEASURED:
   - MEASURED: vessel dimensions (LOA, BEAM, DRAFT from CSV)
   - MEASURED: THIALF displacement (71,368 tonnes from CSV)
   - ASSUMED: Sleipnir/Balder displacement (estimated via default Cb=0.65)
   - ASSUMED: KG = 0.6 * draft for all vessels
   - ASSUMED: Cw = 0.72 (waterplane coefficient)
   - ASSUMED: wind parameters (0.5 kPa, 5000 m^2 projected area, 15m arm)

STEP 3 — (OPTIONAL) IMPROVE SEMI-SUB ESTIMATES:
7. If stability results are physically unreasonable with monohull defaults,
   consider adding vessel_subtype-aware defaults to estimate_vessel_hydrostatics():
   - semi_submersible: Cb_default=0.50, Cw_default=0.55
   - This is a judgment call — only implement if GM values are clearly wrong

STEP 4 — VERIFY:
8. Run: cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
9. Run: cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short
10. Confirm: at least 3 vessels produce non-trivial StabilityResult
11. Confirm: all tests pass or expected failures are documented

ACCEPTANCE CRITERIA:
- AC-1: At least 3 real construction vessels (Sleipnir, Thialf, Balder) produce non-trivial stability results
- AC-2: Semi-submersible vessels pass/fail IMO criteria as expected for SEMISUB type
- AC-3: Tests document assumed vs measured parameters clearly (in docstrings or parametrize IDs)
- AC-4: All new tests pass when run with uv run python -m pytest

CROSS-REVIEW REQUIREMENTS:
- Per AGENTS.md: Route B/C requires cross-review before completion
- Run the full naval_architecture test suite to confirm no regressions
- Verify CSV path resolution works from test file location
```

---

## 6. Verification Commands

```bash
# 1. Verify test file exists and has expected content
grep -c "class Test" digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py

# 2. Run fleet adapter tests
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short

# 3. Run full naval arch suite
cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short

# 4. Verify CSV accessibility
wc -l worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv

# 5. Quick stability sanity check for Balder
cd digitalmodel && uv run python -c "
from digitalmodel.naval_architecture.ship_data import register_fleet_vessels, get_ship, estimate_vessel_hydrostatics
BALDER = {'VESSEL_NAME': 'BALDER', 'LOA_M': 152.0, 'BEAM_M': 76.8, 'DRAFT_M': 25.0}
register_fleet_vessels([BALDER])
h = estimate_vessel_hydrostatics(get_ship('BALDER'))
print(h)
"

# 6. Grep for BALDER in tests (post-implementation)
grep -n "BALDER" digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
```

---

## 7. Final Recommendation

**ALREADY MOSTLY DONE** -- with targeted delta work remaining.

The infrastructure (fleet adapter, stability engine, IMO criteria, test framework) is fully implemented.
The remaining work is **test-only** and is bounded to ~80-120 lines of new test code in a single file:

1. Add `BALDER_RECORD` fixture (8 lines)
2. Add CSV bulk-registration test class (15 lines)
3. Add parametrized 3-vessel stability test class with physical reasonableness checks (60-80 lines)
4. Add assumed-vs-measured parameter documentation in test docstrings

**Estimated effort**: 1-2 hours for a focused implementation session.

**Gate status**: Issue #2059 needs `status:plan-review` label applied, then user approval to `status:plan-approved` before implementation can proceed per AGENTS.md workflow.

---

**RECOMMENDATION: READY AFTER LABEL UPDATE**
