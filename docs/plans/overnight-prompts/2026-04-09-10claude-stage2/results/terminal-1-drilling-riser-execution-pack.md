# Execution Pack: Issue #2063 — Wire Drilling Riser Components into Mooring/Riser Analysis

| Field | Value |
|---|---|
| Issue | [#2063](https://github.com/vamseeachanta/workspace-hub/issues/2063) |
| Title | feat(naval-arch): wire drilling riser components into mooring/riser analysis |
| Labels (current) | `enhancement`, `cat:engineering`, `domain:code-promotion`, `agent:claude` |
| Milestone | None assigned |
| Assignees | None |
| State | OPEN |
| Stage-1 dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md` |
| Pack date | 2026-04-09 |

---

## 1. Fresh Status Check Since Stage-1 Dossier

### 1.1 Verified Repo State (2026-04-09)

| Dossier Claim | Current Reality | Status |
|---|---|---|
| `drilling_riser/` has 4 submodules, 12 exports | 4 submodules, **13** exports in `__all__` (dossier undercounted by 1) | CORRECTED |
| `drilling_riser_components.csv` has 36 records | 36 data rows confirmed (37 lines = 1 header + 36) | CONFIRMED |
| `adapter.py` does not exist | Does not exist — gap is real | CONFIRMED |
| `conftest.py` has shared fixtures | Empty file (whitespace only) — fixtures must be created | CORRECTED |
| `ship_data.py` has `normalize_fleet_record` pattern | Present at line 150, pattern intact | CONFIRMED |
| `DrillingRiserLoader` exists | Present at `worldenergydata/src/worldenergydata/vessel_fleet/loaders/drilling_riser_loader.py` | CONFIRMED |
| Pydantic schemas exist | Present at `worldenergydata/src/worldenergydata/vessel_fleet/schemas/drilling_riser.py` | CONFIRMED |
| #1859 dependency is DONE | Confirmed — adapter pattern established | CONFIRMED |
| No `status:plan-approved` label | Confirmed — still blocked on human review | CONFIRMED |

### 1.2 Dossier Corrections

1. **Export count**: `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` has 13 items in `__all__`, not 12. The full list: `top_tension_required`, `wall_thickness_required`, `effective_tension`, `minimum_slip_ring_tension`, `significant_wave_height_limit`, `operability_fraction`, `watch_circle_radius_m`, `annular_clearance_mm`, `minimum_riser_id_required`, `spacing_requirement_m`, `structural_damping_ratio`, `rayleigh_damping_coefficients`, `modal_damping_equivalent`.

2. **Tension calculation**: The dossier computed 20-joint string tension as 421.98 kN. Correct value: `20 * 3.8 * 4.44822 * 1.25 = 422.58 kN`. The `top_tension_required` function is `submerged_weight_kn * dynamic_factor` where `dynamic_factor` defaults to 1.25.

3. **conftest.py**: Dossier says "add shared fixtures" but the file is empty — no existing fixtures to preserve.

---

## 2. Minimal Plan-Review Packet

### 2.1 Problem Statement

The `digitalmodel.drilling_riser` module has 13 pure calculation functions (stackup, damping, operability, tool passage) but **no way to ingest real component data**. The `worldenergydata` repo has 36 curated drilling riser component records (riser joints, BOPs, LMRPs, flex joints, telescopic joints) in imperial units. The adapter gap prevents end-to-end riser analysis using real equipment specs.

### 2.2 Acceptance Criteria

From the issue body, plus engineering validation:

- [ ] AC-1: Adapter function `normalize_riser_component_record()` converts one CSV row dict (UPPER_SNAKE, imperial) to calculation-ready dict (snake_case, SI: mm, m, kN, MPa)
- [ ] AC-2: Batch function `register_riser_components()` loads all 36 records, returns `(added, skipped)` tuple
- [ ] AC-3: Helper `compute_riser_string_weight_kn()` sums submerged weights for feeding into `top_tension_required()`
- [ ] AC-4: At least one integration test computes riser string weight from real component specs
- [ ] AC-5: Adapter follows the `normalize_*_record` / `register_*` pattern from #1859 (`digitalmodel/src/digitalmodel/naval_architecture/ship_data.py`)
- [ ] AC-6: All 13 existing drilling_riser tests continue to pass (no regressions)

### 2.3 Dependencies

| Dependency | Status | Notes |
|---|---|---|
| #1859 adapter pattern | DONE | `normalize_fleet_record()` at `ship_data.py:150` |
| `drilling_riser_components.csv` | PRESENT | 36 records, imperial units, curated |
| `DrillingRiserLoader` | PRESENT | Query/filter interface ready |
| Pydantic schemas | PRESENT | 5 schemas for validation |
| `digitalmodel.drilling_riser.*` | PRESENT | 13 pure functions, doc-verified tests |

### 2.4 File Paths Expected to Change After Approval

**New files** (in `digitalmodel` subrepo):
1. `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` — normalize + register + string weight functions
2. `digitalmodel/tests/drilling_riser/test_adapter_integration.py` — 6+ integration tests

**Modified files**:
3. `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` — add 3 adapter exports to imports and `__all__`
4. `digitalmodel/tests/drilling_riser/conftest.py` — add shared CSV-loading fixture

**Read-only dependencies** (no changes needed):
5. `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv`
6. `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` (pattern reference only)

---

## 3. Issue Refinement Recommendations

### 3.1 Issue Body Edits Needed

The current issue body is well-structured. Two minor refinements recommended:

**Edit 1 — Add explicit AC for string weight helper**:
In the "Acceptance Criteria" section, after the third bullet, add:
```
- Helper function computes total riser string weight in kN from component list, feeding into `top_tension_required()`
```

**Edit 2 — Add unit conversion note**:
In the "What Needs Doing" section, after item 2, add:
```
3. **Unit conversions**: Adapter converts imperial CSV values (inches, feet, kips, psi) to SI (mm, m, kN, MPa) using plain constants (not pint), following the `ship_data.py` pattern
```

### 3.2 Labels to Add/Remove After Human Review

| Action | Label | Reason |
|---|---|---|
| ADD | `status:plan-review` | Dossier and execution pack ready for human review |
| KEEP | `enhancement` | Correct — new adapter feature |
| KEEP | `cat:engineering` | Correct — engineering calculation domain |
| KEEP | `domain:code-promotion` | Correct — promoting worldenergydata into digitalmodel |
| KEEP | `agent:claude` | Correct — complex TDD implementation |

After human approves the plan:
| Action | Label | Reason |
|---|---|---|
| REMOVE | `status:plan-review` | Replace with approved |
| ADD | `status:plan-approved` | Gate for implementation |

---

## 4. Operator Command Pack

> **DRAFT ONLY — do not execute. These are templates for the human operator.**

### 4.1 Post Summary Comment on Issue

```bash
gh issue comment 2063 --body "$(cat <<'EOF'
## Stage-2 Execution Pack Complete

**Dossier**: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-1-drilling-riser-analysis.md`
**Execution pack**: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-1-drilling-riser-execution-pack.md`

### Fresh Status (2026-04-09)
- All dossier claims verified against repo — 2 minor corrections (export count: 13 not 12; tension calc: 422.58 not 421.98 kN)
- `adapter.py` gap confirmed — no adapter connects worldenergydata CSV to calculation module
- #1859 dependency DONE, adapter pattern established in `ship_data.py`
- CSV data (36 records), loader, schemas all present and validated

### Scope
- 2 new files: `adapter.py` + `test_adapter_integration.py`
- 2 modified files: `__init__.py` (3 new exports) + `conftest.py` (CSV fixture)
- TDD-first, cross-review required per workspace-hub policy

### Next Step
Apply `status:plan-review` label, review the execution pack, then `status:plan-approved` to unblock implementation.
EOF
)"
```

### 4.2 Edit Issue Body (Optional Refinements)

```bash
gh issue edit 2063 --body "$(cat <<'EOF'
## Context
worldenergydata has `drilling_riser_components.csv` with **36 components** (riser joints, BOPs, LMRPs, flex joints) with physical specs (weight, OD, length). These should feed into any existing mooring/riser analysis modules in digitalmodel.

This is part of the #1859 integration roadmap — wiring worldenergydata vessel/equipment data into engineering calculation modules.

## What Needs Doing
1. **Identify target modules** in digitalmodel that perform riser or mooring analysis
2. **Build an adapter** (following the #1859 pattern) that normalizes riser component records into the expected input shape
3. **Unit conversions**: Adapter converts imperial CSV values (inches, feet, kips, psi) to SI (mm, m, kN, MPa) using plain constants (not pint), following the `ship_data.py` pattern
4. **Create test cases** using real component specs (e.g., 21" marine riser joint, 18-3/4" BOP)
5. **Validate** that riser string weight calculations produce physically reasonable results

## Data Available
- `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` — 36 records
- `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_riser.py` — dataclass model
- `worldenergydata/src/worldenergydata/vessel_fleet/loaders/drilling_riser_loader.py` — loader

## Acceptance Criteria
- Riser component adapter normalizes OD, weight, length into calculation-ready units
- At least one integration test computes riser string weight from real component specs
- Helper function computes total riser string weight in kN from component list, feeding into `top_tension_required()`
- Adapter follows the same `normalize_*_record` / `register_*` pattern from #1859

## Depends On
- #1859 (adapter pattern) — DONE
EOF
)"
```

### 4.3 Label Commands (Draft Only)

```bash
# Step 1: Add plan-review label (after human reads this pack)
gh issue edit 2063 --add-label "status:plan-review"

# Step 2: After human approves plan, swap labels
gh issue edit 2063 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

---

## 5. Self-Contained Future Implementation Prompt

```
You are implementing GitHub issue #2063: "Wire drilling riser components into mooring/riser analysis."
Do NOT ask the user any questions. Execute the full TDD cycle below.

## Context
- The worldenergydata CSV at `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` has 36 drilling riser component records (riser joints, BOPs, LMRPs, flex joints, telescopic joints) with imperial units.
- The digitalmodel calculation module at `digitalmodel/src/digitalmodel/drilling_riser/` has 13 pure functions for stackup, damping, operability, and tool passage.
- The established adapter pattern from #1859 is in `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` — functions `normalize_fleet_record()` (line 150) and `register_fleet_vessels()` (line 200).
- There is NO existing adapter connecting the CSV data to the calculation module.
- The `conftest.py` at `digitalmodel/tests/drilling_riser/conftest.py` is empty — create fixtures from scratch.

## TDD Step 1: Write Failing Tests

Create `digitalmodel/tests/drilling_riser/test_adapter_integration.py`:

```python
"""Integration tests — drilling riser adapter wiring worldenergydata CSV to calculation module."""

import pytest
from digitalmodel.drilling_riser.adapter import (
    normalize_riser_component_record,
    register_riser_components,
    compute_riser_string_weight_kn,
)

# --- Unit conversion constants (for test assertions) ---
_KIPS_TO_KN = 4.44822
_IN_TO_MM = 25.4
_FT_TO_M = 0.3048
_PSI_TO_MPA = 0.00689476


class TestNormalizeRiserJoint:
    """Test normalize_riser_component_record with riser joint records."""

    def test_21in_bare_joint(self):
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
        assert result["component_type"] == "riser_joint"
        assert result["od_mm"] == pytest.approx(533.4, rel=0.01)
        assert result["id_mm"] == pytest.approx(495.3, rel=0.01)
        assert result["wall_thickness_mm"] == pytest.approx(19.05, rel=0.01)
        assert result["submerged_weight_kn"] == pytest.approx(3.8 * _KIPS_TO_KN, rel=0.01)
        assert result["length_m"] == pytest.approx(22.86, rel=0.01)
        assert result["pressure_mpa"] == pytest.approx(5000.0 * _PSI_TO_MPA, rel=0.01)

    def test_missing_component_id_returns_none(self):
        record = {"COMPONENT_TYPE": "riser_joint", "OD_IN": 21.0}
        assert normalize_riser_component_record(record) is None


class TestNormalizeBOP:
    """Test normalize_riser_component_record with BOP records."""

    def test_18_75in_bop(self):
        record = {
            "COMPONENT_ID": "BOP-SUB-18.75-15K",
            "COMPONENT_TYPE": "bop",
            "WEIGHT_AIR_KIPS": 400.0, "WEIGHT_WATER_KIPS": 340.0,
            "BORE_SIZE_IN": 18.75, "HEIGHT_FT": 35.0,
            "PRESSURE_RATING_PSI": 15000.0,
        }
        result = normalize_riser_component_record(record)
        assert result is not None
        assert result["component_type"] == "bop"
        assert result["submerged_weight_kn"] == pytest.approx(340.0 * _KIPS_TO_KN, rel=0.01)
        assert result["height_m"] == pytest.approx(35.0 * _FT_TO_M, rel=0.01)
        assert result["bore_size_mm"] == pytest.approx(18.75 * _IN_TO_MM, rel=0.01)


class TestRegisterRiserComponents:
    """Test batch registration of riser components."""

    def test_register_all_36(self, all_csv_records):
        added, skipped = register_riser_components(all_csv_records)
        assert added + skipped == 36
        assert added >= 33  # some may skip due to missing fields


class TestComputeRiserStringWeight:
    """Test riser string weight aggregation."""

    def test_20_bare_joints(self):
        components = [{"submerged_weight_kn": 3.8 * _KIPS_TO_KN}] * 20
        total = compute_riser_string_weight_kn(components)
        assert total == pytest.approx(20 * 3.8 * _KIPS_TO_KN, rel=0.01)

    def test_string_weight_feeds_top_tension(self):
        from digitalmodel.drilling_riser.stackup import top_tension_required
        total_submerged_kn = 20 * 3.8 * _KIPS_TO_KN  # 338.06 kN
        tension = top_tension_required(total_submerged_kn)
        assert tension == pytest.approx(20 * 3.8 * _KIPS_TO_KN * 1.25, rel=0.01)


class TestToolPassageIntegration:
    """Integration: real component specs through tool passage calculation."""

    def test_21in_joint_vs_12_25in_bit(self):
        from digitalmodel.drilling_riser.tool_passage import annular_clearance_mm
        riser_id_mm = 19.5 * _IN_TO_MM  # 495.3 mm
        tool_od_mm = 12.25 * _IN_TO_MM  # 311.15 mm
        clearance = annular_clearance_mm(riser_id_mm, tool_od_mm)
        assert clearance == pytest.approx(92.075, rel=0.01)
        assert clearance > 0  # tool must fit
```

Add CSV fixture to `digitalmodel/tests/drilling_riser/conftest.py`:

```python
"""Shared fixtures for drilling riser tests."""

import csv
from pathlib import Path

import pytest

_CSV_PATH = (
    Path(__file__).resolve().parents[3]
    / "worldenergydata"
    / "data"
    / "modules"
    / "vessel_fleet"
    / "curated"
    / "drilling_riser_components.csv"
)


@pytest.fixture
def all_csv_records():
    """Load all 36 drilling riser component records from worldenergydata CSV."""
    # Resolve relative to workspace-hub root if in-tree
    csv_path = _CSV_PATH
    if not csv_path.exists():
        # Fallback: try from workspace-hub root
        csv_path = Path.cwd() / "worldenergydata" / "data" / "modules" / "vessel_fleet" / "curated" / "drilling_riser_components.csv"
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        records = list(reader)
    assert len(records) == 36, f"Expected 36 records, got {len(records)}"
    return records
```

Run tests — confirm they fail with `ModuleNotFoundError: No module named 'digitalmodel.drilling_riser.adapter'`.

## TDD Step 2: Implement Adapter

Create `digitalmodel/src/digitalmodel/drilling_riser/adapter.py`:

Follow the `normalize_fleet_record` / `register_fleet_vessels` pattern from `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` (lines 150-229). Key design:

- `_KIPS_TO_KN = 4.44822`
- `_IN_TO_MM = 25.4`
- `_FT_TO_M = 0.3048`
- `_PSI_TO_MPA = 0.00689476`
- `normalize_riser_component_record(record: Mapping[str, Any]) -> Optional[dict[str, Any]]`
  - Returns None if COMPONENT_ID is missing or blank
  - Converts all imperial fields to SI using plain multiplication (no pint)
  - Preserves COMPONENT_TYPE, GRADE, DATA_SOURCE as lowercase metadata
  - Handles component-type-specific fields: riser joints have OD/ID/wall_thickness/length; BOPs have bore_size/height; flex joints have max_angle/stiffness; telescopic joints have stroke
- `register_riser_components(records: Iterable[Mapping[str, Any]], *, registry: dict | None = None) -> tuple[int, int]`
  - Normalize all records, store in registry dict keyed by component_id
  - Return (added, skipped)
- `compute_riser_string_weight_kn(components: Iterable[dict]) -> float`
  - Sum `submerged_weight_kn` across all components
  - Raise ValueError if any component lacks `submerged_weight_kn`

## TDD Step 3: Update __init__.py

Add to `digitalmodel/src/digitalmodel/drilling_riser/__init__.py`:

```python
from digitalmodel.drilling_riser.adapter import (
    compute_riser_string_weight_kn,
    normalize_riser_component_record,
    register_riser_components,
)
```

Add to `__all__`:
```python
"normalize_riser_component_record",
"register_riser_components",
"compute_riser_string_weight_kn",
```

## TDD Step 4: Verify

```bash
# All drilling_riser tests (existing + new)
cd digitalmodel && uv run pytest tests/drilling_riser/ -v

# Only new adapter tests
cd digitalmodel && uv run pytest tests/drilling_riser/test_adapter_integration.py -v

# Regression check — existing tests untouched
cd digitalmodel && uv run pytest tests/drilling_riser/test_stackup_doc_verified.py tests/drilling_riser/test_damping_doc_verified.py tests/drilling_riser/test_operability_doc_verified.py tests/drilling_riser/test_tool_passage_doc_verified.py -v

# Import check
cd digitalmodel && uv run python -c "from digitalmodel.drilling_riser.adapter import normalize_riser_component_record, register_riser_components, compute_riser_string_weight_kn; print('OK')"

# Smoke test with real values
cd digitalmodel && uv run python -c "
from digitalmodel.drilling_riser.adapter import normalize_riser_component_record
rec = {'COMPONENT_ID': 'RJ-21-75-BARE', 'COMPONENT_TYPE': 'riser_joint', 'OD_IN': 21.0, 'ID_IN': 19.5, 'WALL_THICKNESS_IN': 0.75, 'LENGTH_FT': 75.0, 'WEIGHT_AIR_KIPS': 22.5, 'WEIGHT_WATER_KIPS': 3.8, 'GRADE': 'X-80', 'PRESSURE_RATING_PSI': 5000.0}
result = normalize_riser_component_record(rec)
print(f'OD: {result[\"od_mm\"]:.1f} mm, Weight: {result[\"submerged_weight_kn\"]:.2f} kN')
assert abs(result['od_mm'] - 533.4) < 1.0
print('PASS')
"
```

## Cross-Review Requirements

Per workspace-hub policy (Route B/C), cross-review is required before completion:
1. After all tests pass, run the cross-review gate
2. Post summary comment on #2063 with implementation details

## Commit Message Template

```
feat(drilling-riser): add worldenergydata adapter for riser components (#2063)

Wire 36 drilling riser component records (joints, BOPs, LMRPs, flex/telescopic
joints) from worldenergydata CSV into digitalmodel calculation module.

- normalize_riser_component_record: imperial-to-SI unit conversion
- register_riser_components: batch load with registry pattern from #1859
- compute_riser_string_weight_kn: aggregate submerged weights for tension calc
- 6 integration tests covering joints, BOPs, string weight, tool passage
```
```

---

## 6. Morning Handoff

### 6.1 What Is Ready Now

- Stage-1 dossier fully verified against current repo state
- All prerequisite code exists: 13 calculation functions, 36 CSV records, loader, schemas, adapter pattern
- Implementation scope is small and well-defined: 2 new files + 2 small edits
- TDD test suite pre-written with correct expected values (corrected from dossier)
- Self-contained implementation prompt ready for copy-paste dispatch
- Draft `gh` commands ready for operator review

### 6.2 What Still Blocks Implementation

| Blocker | Owner | Action |
|---|---|---|
| `status:plan-approved` label not set | Human operator | Review this pack, then run label commands from Section 4.3 |
| No milestone assigned | Human operator | Optional — assign to relevant milestone if desired |
| Cross-review gate | Post-implementation | Required after implementation, not a pre-blocker |

### 6.3 Estimated Scope

- **Files to create**: 2 (adapter.py ~80 lines, test_adapter_integration.py ~90 lines)
- **Files to modify**: 2 (__init__.py +6 lines, conftest.py +20 lines)
- **Net new code**: ~190 lines
- **Risk**: Low — follows established pattern, no API changes, read-only worldenergydata dependency

---

## 7. Final Recommendation

**READY FOR PLAN REVIEW**

All prerequisite code is in place. The implementation is a focused 2-file addition following the proven #1859 adapter pattern. The stage-1 dossier has been verified and corrected (export count: 13, tension calc: 422.58 kN). The only blocker is the `status:plan-approved` label, which requires human review of this execution pack.
