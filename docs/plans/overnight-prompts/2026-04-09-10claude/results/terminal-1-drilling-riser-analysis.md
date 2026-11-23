# Dossier: Issue #2063 — Wire Drilling Riser Components into Mooring/Riser Analysis

| Field | Value |
|---|---|
| Issue | [#2063](https://github.com/vamseeachanta/workspace-hub/issues/2063) |
| Labels | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| Depends on | #1859 (adapter pattern) — DONE |
| Date | 2026-04-09 |
| Status | Implementation-ready pending `status:plan-approved` label |

---

## 1. Current-State Findings

### 1.1 Calculation Module (COMPLETE)

The `digitalmodel/src/digitalmodel/drilling_riser/` module is fully implemented with 4 submodules and 12 exported functions:

| File | Functions | Status |
|---|---|---|
| `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | 12 exports | Complete |
| `digitalmodel/src/digitalmodel/drilling_riser/stackup.py` | `top_tension_required`, `wall_thickness_required`, `effective_tension`, `minimum_slip_ring_tension` | Complete |
| `digitalmodel/src/digitalmodel/drilling_riser/damping.py` | `structural_damping_ratio`, `rayleigh_damping_coefficients`, `modal_damping_equivalent` | Complete |
| `digitalmodel/src/digitalmodel/drilling_riser/operability.py` | `significant_wave_height_limit`, `operability_fraction`, `watch_circle_radius_m` | Complete |
| `digitalmodel/src/digitalmodel/drilling_riser/tool_passage.py` | `annular_clearance_mm`, `minimum_riser_id_required`, `spacing_requirement_m` | Complete |

**Key standards referenced**: API RP 16Q, 2H-TNE-0050-03, API SPEC 16F, 50043-PRS-0001-1 (DeepStar).

### 1.2 Unit Tests (COMPLETE)

| File | Tests |
|---|---|
| `digitalmodel/tests/drilling_riser/test_stackup_doc_verified.py` | 13 tests across 4 classes |
| `digitalmodel/tests/drilling_riser/test_damping_doc_verified.py` | 10 tests across 3 classes |
| `digitalmodel/tests/drilling_riser/test_operability_doc_verified.py` | ~8 tests |
| `digitalmodel/tests/drilling_riser/test_tool_passage_doc_verified.py` | ~6 tests |

Test fixtures exist at `digitalmodel/tests/fixtures/test_vectors/drilling/drilling_riser_*.yaml`.

### 1.3 Source Data (COMPLETE)

| File | Description |
|---|---|
| `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` | 36 records: 22 riser_joints, 5 BOPs, 3 LMRPs, 4 flex_joints, 3 telescopic_joints |
| `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_riser.py` | 5 dataclasses: `RiserJointEntry`, `BOPEntry`, `LMRPEntry`, `FlexJointEntry`, `TelescopicJointEntry` |
| `worldenergydata/src/worldenergydata/vessel_fleet/loaders/drilling_riser_loader.py` | `DrillingRiserLoader` with query/filter methods |
| `worldenergydata/src/worldenergydata/vessel_fleet/schemas/drilling_riser.py` | 5 Pydantic schemas for validation |

CSV columns relevant to calculation inputs:
- **Riser joints**: `COMPONENT_ID`, `OD_IN`, `ID_IN`, `WALL_THICKNESS_IN`, `LENGTH_FT`, `WEIGHT_AIR_KIPS`, `WEIGHT_WATER_KIPS`, `GRADE`, `BUOYANCY_COVERAGE_PCT`, `PRESSURE_RATING_PSI`
- **BOPs/LMRPs**: `WEIGHT_AIR_KIPS`, `WEIGHT_WATER_KIPS`, `HEIGHT_FT`, `BORE_SIZE_IN`, `PRESSURE_RATING_PSI`
- **Flex joints**: `WEIGHT_AIR_KIPS`, `MAX_ANGLE_DEG`, `STIFFNESS_FT_KIP_PER_DEG`
- **Telescopic joints**: `OD_IN`, `STROKE_FT`, `WEIGHT_AIR_KIPS`

### 1.4 Adapter Pattern (DONE — from #1859)

The established pattern lives in `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`:

```python
# Pattern 1: normalize single record
def normalize_fleet_record(record: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    """Convert worldenergydata record (UPPER_SNAKE, metric) to registry shape."""
    name = record.get("VESSEL_NAME")
    if not isinstance(name, str) or not name.strip():
        return None
    entry = { ... converted fields ... }
    entry = {k: v for k, v in entry.items() if v is not None}
    return entry

# Pattern 2: batch register
def register_fleet_vessels(records, *, overwrite=False) -> tuple[int, int]:
    """Normalize all records and merge into registry."""
    ...
    return added, skipped
```

A second adapter `normalize_drilling_rig_record()` exists in the same file for rig records.

### 1.5 Existing Stack-Up Calculator (LEGACY)

`digitalmodel/src/digitalmodel/infrastructure/base_solvers/marine/typical_riser_stack_up_calculations.py` is a pandas/pint-based OOP riser string assembly calculator. It reads component tables with columns like `Component`, `Component Length`, `No. Of. Joints` and computes elevations, weights, tensions, and stretch. This is the **downstream consumer** that would benefit from worldenergydata component records, but wiring to it is a stretch goal beyond #2063.

### 1.6 Related Commits

| Commit | Description |
|---|---|
| `c41e53adb` (2026-02-24) | `feat(wrk-425-430): implement lifecycle cost and AMJIG drilling riser integrity calculations` — created the drilling_riser module |
| `bdf48030c` | `feat(WRK-1113): drilling_riser doc-extracts + submodule pointer` |
| No commits reference `#2063` yet | |

---

## 2. Remaining Implementation Delta

### 2.1 What is MISSING

The central gap: **no adapter exists** that converts worldenergydata drilling riser component CSV records into the input shapes expected by `digitalmodel.drilling_riser.*` functions.

| Missing Behavior | Description |
|---|---|
| `normalize_riser_component_record()` | Convert CSV row dict (UPPER_SNAKE, imperial) to calculation-ready dict (SI units: mm for OD, kN for weight, m for length) |
| `register_riser_components()` | Batch-load + normalize all 36 records from worldenergydata |
| `compute_riser_string_weight()` | Sum submerged weights of N joints + BOP + LMRP to get total submerged weight in kN — feeds into `top_tension_required()` |
| Integration test: string weight | Use real specs (e.g., 20x 21" bare joints + 1x 18-3/4" BOP + 1x LMRP) to compute weight and tension |
| Integration test: tool passage | Use real OD/ID to validate annular clearance against real tool OD |

### 2.2 Unit Conversion Requirements

The adapter must convert:
- `WEIGHT_WATER_KIPS` (kips) -> `submerged_weight_kn` (kN): multiply by 4.44822
- `OD_IN` (inches) -> `od_mm` (mm): multiply by 25.4
- `ID_IN` (inches) -> `id_mm` (mm): multiply by 25.4
- `WALL_THICKNESS_IN` (inches) -> `wall_thickness_mm` (mm): multiply by 25.4
- `LENGTH_FT` (feet) -> `length_m` (m): multiply by 0.3048
- `PRESSURE_RATING_PSI` (psi) -> `pressure_mpa` (MPa): multiply by 0.00689476
- `WEIGHT_AIR_KIPS` (kips) -> `weight_air_kn` (kN): multiply by 4.44822

### 2.3 Exact File Paths That Should Change

**New files** (in `digitalmodel`):
1. `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` — normalize + register functions
2. `digitalmodel/tests/drilling_riser/test_adapter_integration.py` — integration tests with real CSV data

**Modified files**:
3. `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` — add adapter exports
4. `digitalmodel/tests/drilling_riser/conftest.py` — add shared fixtures for CSV loading

---

## 3. TDD-First Execution Plan

### Phase 1: Failing Tests First

**File**: `digitalmodel/tests/drilling_riser/test_adapter_integration.py`

```python
# Test 1: normalize_riser_component_record converts a 21" bare joint
def test_normalize_riser_joint_21in_bare():
    record = {
        "COMPONENT_ID": "RJ-21-75-BARE",
        "COMPONENT_TYPE": "riser_joint",
        "OD_IN": 21.0, "ID_IN": 19.5, "WALL_THICKNESS_IN": 0.75,
        "LENGTH_FT": 75.0, "WEIGHT_AIR_KIPS": 22.5,
        "WEIGHT_WATER_KIPS": 3.8, "GRADE": "X-80",
        "PRESSURE_RATING_PSI": 5000.0,
    }
    result = normalize_riser_component_record(record)
    assert result is not None
    assert result["component_id"] == "RJ-21-75-BARE"
    assert result["od_mm"] == pytest.approx(533.4, rel=0.01)
    assert result["submerged_weight_kn"] == pytest.approx(16.903, rel=0.02)
    assert result["length_m"] == pytest.approx(22.86, rel=0.01)
    assert result["pressure_mpa"] == pytest.approx(34.47, rel=0.02)

# Test 2: normalize_riser_component_record handles BOP (no OD fields)
def test_normalize_bop_record():
    record = {
        "COMPONENT_ID": "BOP-SUB-18.75-15K",
        "COMPONENT_TYPE": "bop",
        "WEIGHT_AIR_KIPS": 400.0, "WEIGHT_WATER_KIPS": 340.0,
        "BORE_SIZE_IN": 18.75, "HEIGHT_FT": 35.0,
        "PRESSURE_RATING_PSI": 15000.0,
    }
    result = normalize_riser_component_record(record)
    assert result["submerged_weight_kn"] == pytest.approx(1512.39, rel=0.02)
    assert result["height_m"] == pytest.approx(10.668, rel=0.01)

# Test 3: riser string weight from real component specs
def test_riser_string_weight_20_bare_joints():
    """20x 21" bare joints -> total submerged = 20 * 3.8 kips = 76.0 kips = 338.06 kN."""
    from digitalmodel.drilling_riser.stackup import top_tension_required
    total_submerged_kn = 20 * 3.8 * 4.44822  # 20 bare joints
    tension = top_tension_required(total_submerged_kn)
    assert tension == pytest.approx(421.98, rel=0.02)  # 338.06 * 1.25

# Test 4: register_riser_components loads all 36 records
def test_register_riser_components_all_36():
    added, skipped = register_riser_components(all_records)
    assert added + skipped == 36
    assert added >= 33  # some may skip due to missing fields

# Test 5: tool passage clearance with real 21" joint ID vs 12-1/4" bit
def test_tool_passage_real_specs():
    from digitalmodel.drilling_riser.tool_passage import annular_clearance_mm
    riser_id_mm = 19.5 * 25.4  # 495.3 mm
    tool_od_mm = 12.25 * 25.4  # 311.15 mm
    clearance = annular_clearance_mm(riser_id_mm, tool_od_mm)
    assert clearance == pytest.approx(92.075, rel=0.01)
    assert clearance > 0  # tool must fit

# Test 6: wall thickness validation with real component specs
def test_wall_thickness_21in_joint():
    from digitalmodel.drilling_riser.stackup import wall_thickness_required
    result = wall_thickness_required(
        od_mm=21.0 * 25.4,  # 533.4 mm
        design_pressure_mpa=5000.0 * 0.00689476,  # 34.47 MPa
        smys_mpa=552.0,  # X-80 grade
    )
    # Actual wall thickness is 0.75" = 19.05mm. Required should be less.
    assert result < 19.05  # confirms actual thickness exceeds minimum
```

### Phase 2: Implementation

1. **Create `digitalmodel/src/digitalmodel/drilling_riser/adapter.py`**:
   - `_KIPS_TO_KN = 4.44822`
   - `_IN_TO_MM = 25.4`
   - `_FT_TO_M = 0.3048`
   - `_PSI_TO_MPA = 0.00689476`
   - `normalize_riser_component_record(record: Mapping) -> Optional[dict]` — converts one CSV row
   - `register_riser_components(records: list, *, registry=None) -> tuple[int, int]` — batch normalize and store
   - `compute_riser_string_weight_kn(components: list[dict]) -> float` — sum submerged weights

2. **Update `digitalmodel/src/digitalmodel/drilling_riser/__init__.py`**:
   - Add imports: `normalize_riser_component_record`, `register_riser_components`, `compute_riser_string_weight_kn`
   - Add to `__all__`

3. **Create `digitalmodel/tests/drilling_riser/test_adapter_integration.py`** with tests above

4. **Update `digitalmodel/tests/drilling_riser/conftest.py`** with fixtures for loading CSV data

### Phase 3: Verification Commands

```bash
# 1. Run all drilling_riser tests (existing + new)
cd digitalmodel && uv run pytest tests/drilling_riser/ -v

# 2. Run only new adapter integration tests
cd digitalmodel && uv run pytest tests/drilling_riser/test_adapter_integration.py -v

# 3. Verify all existing tests still pass (no regressions)
cd digitalmodel && uv run pytest tests/drilling_riser/test_stackup_doc_verified.py tests/drilling_riser/test_damping_doc_verified.py tests/drilling_riser/test_operability_doc_verified.py tests/drilling_riser/test_tool_passage_doc_verified.py -v

# 4. Import check — adapter loads without errors
cd digitalmodel && uv run python -c "from digitalmodel.drilling_riser.adapter import normalize_riser_component_record, register_riser_components; print('OK')"

# 5. Smoke test — normalize a real component
cd digitalmodel && uv run python -c "
from digitalmodel.drilling_riser.adapter import normalize_riser_component_record
rec = {'COMPONENT_ID': 'RJ-21-75-BARE', 'COMPONENT_TYPE': 'riser_joint', 'OD_IN': 21.0, 'ID_IN': 19.5, 'WALL_THICKNESS_IN': 0.75, 'LENGTH_FT': 75.0, 'WEIGHT_AIR_KIPS': 22.5, 'WEIGHT_WATER_KIPS': 3.8, 'GRADE': 'X-80', 'PRESSURE_RATING_PSI': 5000.0}
result = normalize_riser_component_record(rec)
print(f'OD: {result[\"od_mm\"]:.1f} mm, Weight: {result[\"submerged_weight_kn\"]:.2f} kN')
assert abs(result['od_mm'] - 533.4) < 1.0
print('PASS')
"

# 6. Verify CSV data accessible from worldenergydata
uv run python -c "
import pandas as pd
df = pd.read_csv('worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv')
print(f'Records: {len(df)}, Types: {df.COMPONENT_TYPE.value_counts().to_dict()}')
assert len(df) >= 36
print('PASS')
"
```

---

## 4. Risk / Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Status | Resolution |
|---|---|---|
| `status:plan-approved` label required | NOT SET | User must review this dossier and apply `status:plan-approved` to #2063 |
| #1859 dependency | DONE | Adapter pattern established in `ship_data.py` |

### 4.2 Data / Source Dependencies

| Dependency | Status | Risk |
|---|---|---|
| `drilling_riser_components.csv` (36 records) | Present, validated | Low — data is curated and has Pydantic schemas |
| `DrillingRiserLoader` in worldenergydata | Present | Low — mature loader with query interface |
| `digitalmodel.drilling_riser.*` calculation functions | Present (12 functions) | Low — well-tested with doc-verified tests |
| `pint` UnitRegistry (`digitalmodel.units`) | Present | Low — `ureg` and `Q_` available, but adapter should use plain constants for simplicity (follow `ship_data.py` pattern which uses `_M_TO_FT` constants, not pint) |

### 4.3 Merge / Contention Concerns

| Concern | Risk Level | Mitigation |
|---|---|---|
| `drilling_riser/__init__.py` modification | Low | Only adding imports; no conflict expected |
| `worldenergydata` submodule pointer | None | No changes needed in worldenergydata — only reading existing CSV |
| `digitalmodel` submodule | Medium | Changes are in digitalmodel repo; need to commit there first, then update submodule pointer in workspace-hub |
| Parallel terminal work (terminals 2-10) | Low | No overlap — terminal-2 is drilling rig fleet (different data), others are different domains |

### 4.4 Engineering Risk Assessment

- **Physical reasonableness**: The 21" bare riser joint at 3.8 kips submerged / 75 ft joint is ~50.7 lb/ft submerged weight. For a steel pipe with OD 21" and WT 0.75" in seawater, this is physically reasonable (cross-check: steel weight ~490 lb/ft^3, displaced seawater ~64 lb/ft^3, pipe area ~47.6 in^2, buoyancy area ~346.4 in^2).
- **Unit consistency**: All worldenergydata CSV values are in imperial (inches, feet, kips, psi). The adapter must convert to SI for the calculation module (mm, m, kN, MPa). This is the same pattern as `normalize_fleet_record` which converts metric to imperial for the ship registry.

---

## 5. Ready-to-Execute Prompt

```
You are implementing GitHub issue #2063: "Wire drilling riser components into mooring/riser analysis."

## Context
- The worldenergydata CSV at `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` has 36 drilling riser component records (riser joints, BOPs, LMRPs, flex joints, telescopic joints) with imperial units.
- The digitalmodel calculation module at `digitalmodel/src/digitalmodel/drilling_riser/` has 12 pure functions for stackup, damping, operability, and tool passage.
- The established adapter pattern from #1859 is in `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` — functions `normalize_fleet_record()` and `register_fleet_vessels()`.
- There is NO existing adapter connecting the CSV data to the calculation module.

## What to Build (TDD)

### Step 1: Write failing tests in `digitalmodel/tests/drilling_riser/test_adapter_integration.py`
- Test `normalize_riser_component_record()` with a 21" bare joint record (verify od_mm=533.4, submerged_weight_kn=16.903, length_m=22.86)
- Test `normalize_riser_component_record()` with an 18-3/4" BOP record (verify submerged_weight_kn=1512.39, height_m=10.668)
- Test `register_riser_components()` loads all 36 records (added + skipped == 36, added >= 33)
- Test `compute_riser_string_weight_kn()` for 20x bare 21" joints -> total 338.06 kN
- Test integration: 20-joint string weight fed into `top_tension_required()` -> 422.58 kN
- Test tool passage: 21" joint ID (19.5" = 495.3mm) vs 12-1/4" bit (311.15mm) -> clearance 92.075mm

### Step 2: Implement `digitalmodel/src/digitalmodel/drilling_riser/adapter.py`
Follow the `normalize_fleet_record` / `register_fleet_vessels` pattern exactly:
- `normalize_riser_component_record(record: Mapping[str, Any]) -> Optional[dict[str, Any]]`
  - Input: CSV row dict with UPPER_SNAKE keys, imperial units
  - Output: dict with snake_case keys, SI units (mm, m, kN, MPa)
  - Returns None if COMPONENT_ID is missing
- `register_riser_components(records: list[Mapping], *, registry=None) -> tuple[int, int]`
  - Normalize all records, store in registry dict keyed by component_id
  - Return (added, skipped)
- `compute_riser_string_weight_kn(components: list[dict]) -> float`
  - Sum submerged_weight_kn across all components
  - Use this to feed into `top_tension_required()`

Unit conversions:
- KIPS_TO_KN = 4.44822
- IN_TO_MM = 25.4
- FT_TO_M = 0.3048
- PSI_TO_MPA = 0.00689476

### Step 3: Update `digitalmodel/src/digitalmodel/drilling_riser/__init__.py`
Add adapter imports to `__init__.py` and `__all__`.

### Step 4: Verify
Run: `cd digitalmodel && uv run pytest tests/drilling_riser/ -v`
Confirm: all existing tests still pass + new adapter tests pass.

## Acceptance Criteria
- [ ] Riser component adapter normalizes OD, weight, length into calculation-ready units
- [ ] At least one integration test computes riser string weight from real component specs
- [ ] Adapter follows the same `normalize_*_record` / `register_*` pattern from #1859
- [ ] All existing drilling_riser tests continue to pass (no regressions)

## Cross-Review Requirements
- Cross-review required per workspace-hub policy (Route B/C)
- After implementation, post summary comment on #2063
```

---

## 6. Final Recommendation

### READY AFTER LABEL UPDATE

**Rationale**: All prerequisite pieces are in place:
- Calculation engine: 12 functions across 4 submodules, all tested
- Source data: 36 curated records with Pydantic validation schemas
- Adapter pattern: Established by #1859, proven with fleet + rig record adapters
- Test vectors: Real component specs available in CSV (21" joints at 22.5 kips air / 3.8 kips water, 18-3/4" BOPs at 400 kips air)

**Only blocker**: Issue #2063 needs the `status:plan-approved` label applied after user reviews this dossier. Implementation is a focused 2-file addition (adapter.py + test_adapter_integration.py) plus a 2-line `__init__.py` update.
