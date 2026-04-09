# Execution Pack: Issue #2063 — Wire Drilling Riser Components into Mooring/Riser Analysis

| Field | Value |
|---|---|
| Issue | [#2063](https://github.com/vamseeachanta/workspace-hub/issues/2063) |
| Labels | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| Depends on | #1859 (adapter pattern) — **DONE** |
| Wave | 1 (high-confidence batch, per follow-up summary) |
| Date | 2026-04-09 |

---

## 1. Executive Summary

Issue #2063 bridges the gap between the 36 curated drilling riser component records in `worldenergydata` (imperial units: inches, feet, kips, psi) and the 12 pure calculation functions in `digitalmodel.drilling_riser` (SI units: mm, m, kN, MPa) by implementing a unit-converting adapter module following the `normalize_*_record` / `register_*` pattern established by #1859. All upstream dependencies are complete: the calculation engine has 37+ doc-verified tests, the source CSV has Pydantic validation schemas, and the adapter pattern is proven in `ship_data.py`. The implementation is a focused 2-file addition plus a 2-line `__init__.py` update with no changes needed in `worldenergydata`.

---

## 2. Exact Scope Approved for Implementation

| Deliverable | Location | Description |
|---|---|---|
| Adapter module | `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` | `normalize_riser_component_record()`, `register_riser_components()`, `compute_riser_string_weight_kn()` |
| Integration tests | `digitalmodel/tests/drilling_riser/test_adapter_integration.py` | 6 tests covering unit conversion, batch registration, string weight, tool passage |
| Init exports | `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | Add adapter imports to `__all__` |
| Test fixtures | `digitalmodel/tests/drilling_riser/conftest.py` | Shared fixtures for CSV loading (if needed) |

### Unit conversion constants (imperial → SI)

| Conversion | Constant | Value |
|---|---|---|
| kips → kN | `_KIPS_TO_KN` | 4.44822 |
| inches → mm | `_IN_TO_MM` | 25.4 |
| feet → m | `_FT_TO_M` | 0.3048 |
| psi → MPa | `_PSI_TO_MPA` | 0.00689476 |

---

## 3. Explicit Out-of-Scope List

| Item | Reason |
|---|---|
| Modifying `worldenergydata` code or CSV data | Read-only consumer; no schema changes needed |
| Wiring adapter output to the legacy `typical_riser_stack_up_calculations.py` pandas/pint calculator | Stretch goal beyond #2063 per dossier §1.5 |
| Adding new component types to the CSV | Data curation is a separate workflow |
| Changes to existing drilling_riser calculation functions (stackup, damping, operability, tool_passage) | These are complete and tested; adapter only feeds data into them |
| Pint-based unit handling in the adapter | Follow `ship_data.py` pattern using plain multiplication constants, not pint |
| Updating the `worldenergydata` submodule pointer | No changes in that repo |
| Any work on #2062 (drilling rig fleet adapter) | Separate issue, lower confidence per follow-up summary |
| Changes to `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Reference pattern only; do not modify |

---

## 4. TDD-First Task Sequence

### Phase 1: Write Failing Tests

Create `digitalmodel/tests/drilling_riser/test_adapter_integration.py` with these tests (all must fail initially since `adapter.py` does not exist):

| # | Test | Key Assertion |
|---|---|---|
| T1 | `test_normalize_riser_joint_21in_bare` | `od_mm ≈ 533.4`, `submerged_weight_kn ≈ 16.903`, `length_m ≈ 22.86`, `pressure_mpa ≈ 34.47` |
| T2 | `test_normalize_bop_record` | `submerged_weight_kn ≈ 1512.39`, `height_m ≈ 10.668` |
| T3 | `test_normalize_returns_none_for_missing_id` | Returns `None` when `COMPONENT_ID` is absent |
| T4 | `test_register_riser_components_all_36` | `added + skipped == 36`, `added >= 33` |
| T5 | `test_riser_string_weight_20_bare_joints` | `compute_riser_string_weight_kn(20 joints) ≈ 338.06 kN` |
| T6 | `test_tool_passage_real_specs` | `annular_clearance_mm(495.3, 311.15) ≈ 92.075` |

### Phase 2: Implement Adapter

1. Create `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` following the `ship_data.py` pattern:
   - `normalize_riser_component_record(record: Mapping[str, Any]) -> Optional[dict[str, Any]]`
   - `register_riser_components(records, *, registry=None) -> tuple[int, int]`
   - `compute_riser_string_weight_kn(components: list[dict]) -> float`
2. Update `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` — add imports and `__all__` entries
3. Update `digitalmodel/tests/drilling_riser/conftest.py` if shared fixtures are needed

### Phase 3: Green Tests

```bash
cd digitalmodel && uv run pytest tests/drilling_riser/ -v
```

All 6 new tests + all ~37 existing tests must pass.

### Phase 4: Verification

```bash
# Regression check — existing tests unchanged
cd digitalmodel && uv run pytest tests/drilling_riser/test_stackup_doc_verified.py \
  tests/drilling_riser/test_damping_doc_verified.py \
  tests/drilling_riser/test_operability_doc_verified.py \
  tests/drilling_riser/test_tool_passage_doc_verified.py -v

# Import smoke test
cd digitalmodel && uv run python -c \
  "from digitalmodel.drilling_riser.adapter import normalize_riser_component_record, register_riser_components, compute_riser_string_weight_kn; print('OK')"

# Physical reasonableness smoke test
cd digitalmodel && uv run python -c "
from digitalmodel.drilling_riser.adapter import normalize_riser_component_record
rec = {'COMPONENT_ID': 'RJ-21-75-BARE', 'COMPONENT_TYPE': 'riser_joint',
       'OD_IN': 21.0, 'ID_IN': 19.5, 'WALL_THICKNESS_IN': 0.75,
       'LENGTH_FT': 75.0, 'WEIGHT_AIR_KIPS': 22.5, 'WEIGHT_WATER_KIPS': 3.8,
       'GRADE': 'X-80', 'PRESSURE_RATING_PSI': 5000.0}
r = normalize_riser_component_record(rec)
assert abs(r['od_mm'] - 533.4) < 1.0, f'OD mismatch: {r[\"od_mm\"]}'
assert abs(r['submerged_weight_kn'] - 16.903) < 0.5, f'Weight mismatch: {r[\"submerged_weight_kn\"]}'
print('PHYSICAL REASONABLENESS: PASS')
"
```

---

## 5. Exact Files Expected to Change

### New files (in `digitalmodel` repo)

| File | Type | Lines (est.) |
|---|---|---|
| `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` | Production | ~60–80 |
| `digitalmodel/tests/drilling_riser/test_adapter_integration.py` | Test | ~80–100 |

### Modified files (in `digitalmodel` repo)

| File | Change | Lines changed (est.) |
|---|---|---|
| `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | Add 3 imports + extend `__all__` | ~3–5 |
| `digitalmodel/tests/drilling_riser/conftest.py` | Add CSV-loading fixture (if needed) | ~5–10 |

### Unchanged (read-only references)

| File | Role |
|---|---|
| `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv` | Source data (36 records) |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Pattern reference only |
| `digitalmodel/src/digitalmodel/drilling_riser/stackup.py` | Called by integration tests |
| `digitalmodel/src/digitalmodel/drilling_riser/tool_passage.py` | Called by integration tests |

---

## 6. Git Contention Notes

| Concern | Risk | Mitigation |
|---|---|---|
| All changes are inside `digitalmodel/` submodule | **Medium** | Must `cd digitalmodel`, commit there first, then update submodule pointer in workspace-hub |
| `drilling_riser/__init__.py` modification | **Low** | Only adding 3 imports — unlikely to conflict with other work |
| Parallel overnight terminals (1–10) | **Low** | Terminal-1 produced the dossier (read-only); terminal-2 was assigned this pack; no other terminal touches `drilling_riser/` |
| Wave 1 peer issues (#2059, #2056) | **None** | #2059 touches `naval_architecture/` tests (different module); #2056 touches governance hooks (different domain entirely) |
| `worldenergydata` submodule pointer | **None** | No changes in worldenergydata — zero contention risk |
| Stale submodule pointer | **Low** | After committing in `digitalmodel/`, update submodule pointer in workspace-hub in a separate commit |

---

## 7. Self-Contained Claude Implementation Prompt

```
You are implementing GitHub issue #2063: "Wire drilling riser components into mooring/riser analysis."

## Context
- Source data: `worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv`
  has 36 drilling riser component records (22 riser_joints, 5 BOPs, 3 LMRPs, 4 flex_joints,
  3 telescopic_joints) with imperial units (inches, feet, kips, psi).
- Calculation module: `digitalmodel/src/digitalmodel/drilling_riser/` has 12 pure functions
  across 4 submodules (stackup, damping, operability, tool_passage).
- Adapter pattern: `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` contains
  `normalize_fleet_record()` and `register_fleet_vessels()` — follow this pattern exactly.
- Gap: NO adapter connects the CSV data to the calculation module. You are building that bridge.

## Step 1: Write failing tests
Create `digitalmodel/tests/drilling_riser/test_adapter_integration.py`:

- test_normalize_riser_joint_21in_bare:
    input: {COMPONENT_ID: "RJ-21-75-BARE", COMPONENT_TYPE: "riser_joint", OD_IN: 21.0,
            ID_IN: 19.5, WALL_THICKNESS_IN: 0.75, LENGTH_FT: 75.0, WEIGHT_AIR_KIPS: 22.5,
            WEIGHT_WATER_KIPS: 3.8, GRADE: "X-80", PRESSURE_RATING_PSI: 5000.0}
    assert: od_mm ≈ 533.4, submerged_weight_kn ≈ 16.903, length_m ≈ 22.86, pressure_mpa ≈ 34.47

- test_normalize_bop_record:
    input: {COMPONENT_ID: "BOP-SUB-18.75-15K", COMPONENT_TYPE: "bop", WEIGHT_AIR_KIPS: 400.0,
            WEIGHT_WATER_KIPS: 340.0, BORE_SIZE_IN: 18.75, HEIGHT_FT: 35.0,
            PRESSURE_RATING_PSI: 15000.0}
    assert: submerged_weight_kn ≈ 1512.39, height_m ≈ 10.668

- test_normalize_returns_none_for_missing_id:
    input: {COMPONENT_TYPE: "riser_joint", OD_IN: 21.0}  (no COMPONENT_ID)
    assert: result is None

- test_register_riser_components_all_36:
    Load all records from drilling_riser_components.csv via pandas
    assert: added + skipped == 36, added >= 33

- test_riser_string_weight_20_bare_joints:
    Build 20 normalized joint dicts with submerged_weight_kn = 3.8 * 4.44822
    assert: compute_riser_string_weight_kn(joints) ≈ 338.06

- test_tool_passage_real_specs:
    from digitalmodel.drilling_riser.tool_passage import annular_clearance_mm
    assert: annular_clearance_mm(19.5 * 25.4, 12.25 * 25.4) ≈ 92.075

Run: cd digitalmodel && uv run pytest tests/drilling_riser/test_adapter_integration.py -v
Confirm: all 6 tests FAIL (ImportError or AssertionError).

## Step 2: Implement adapter
Create `digitalmodel/src/digitalmodel/drilling_riser/adapter.py`:

    _KIPS_TO_KN = 4.44822
    _IN_TO_MM = 25.4
    _FT_TO_M = 0.3048
    _PSI_TO_MPA = 0.00689476

    def normalize_riser_component_record(record: Mapping[str, Any]) -> Optional[dict[str, Any]]:
        """Convert one CSV row (UPPER_SNAKE, imperial) to calculation-ready dict (snake_case, SI).
        Returns None if COMPONENT_ID is missing or empty."""
        - Extract COMPONENT_ID; return None if missing/empty
        - Convert all available fields using constants above
        - Strip None values from output dict
        - Return normalized dict

    def register_riser_components(records, *, registry=None) -> tuple[int, int]:
        """Batch-normalize records and merge into registry dict keyed by component_id."""
        - If registry is None, use module-level _REGISTRY dict
        - Normalize each record; skip if None
        - Return (added, skipped)

    def compute_riser_string_weight_kn(components: list[dict]) -> float:
        """Sum submerged_weight_kn across all components."""
        - Return sum of component["submerged_weight_kn"] for all components

## Step 3: Update __init__.py
Add to `digitalmodel/src/digitalmodel/drilling_riser/__init__.py`:
    from .adapter import normalize_riser_component_record, register_riser_components, compute_riser_string_weight_kn
    Add all three to __all__

## Step 4: Update conftest.py if needed
Add shared fixture to `digitalmodel/tests/drilling_riser/conftest.py` for loading CSV records.

## Step 5: Run ALL drilling_riser tests
    cd digitalmodel && uv run pytest tests/drilling_riser/ -v
Confirm: ALL tests pass (existing ~37 + new 6). Zero regressions.

## Step 6: Commit
    cd digitalmodel
    git add src/digitalmodel/drilling_riser/adapter.py \
            tests/drilling_riser/test_adapter_integration.py \
            src/digitalmodel/drilling_riser/__init__.py \
            tests/drilling_riser/conftest.py
    git commit -m "feat(drilling-riser): add worldenergydata adapter for riser components (#2063)"

Then update submodule pointer in workspace-hub:
    cd /mnt/local-analysis/workspace-hub
    git add digitalmodel
    git commit -m "chore(submodule): update digitalmodel for drilling riser adapter (#2063)"

## Step 7: Post issue comment
Post a summary comment on #2063 per workspace-hub policy.

## Constraints
- Do NOT modify any worldenergydata files
- Do NOT modify existing drilling_riser calculation functions
- Do NOT use pint in the adapter — use plain multiplication constants
- Do NOT wire adapter output to the legacy typical_riser_stack_up_calculations.py
- Follow the normalize_fleet_record / register_fleet_vessels pattern from ship_data.py
```

---

## 8. Approval Checklist

- [ ] Executive summary accurately reflects issue scope
- [ ] All acceptance criteria from #2063 are addressed (adapter normalizes units, integration test for string weight, follows #1859 pattern)
- [ ] Out-of-scope list reviewed — no critical items wrongly excluded
- [ ] TDD sequence starts with failing tests before implementation
- [ ] File list is complete and limited to `digitalmodel/` submodule
- [ ] Git contention analysis confirms no overlap with Wave 1 peers (#2059, #2056)
- [ ] Self-contained prompt is copy-pasteable without additional context
- [ ] Dependency #1859 confirmed DONE
- [ ] Unit conversion constants verified against standard references
- [ ] No changes required in `worldenergydata` repo

---

## 9. Suggested Issue Comment Text

### For `status:plan-review` label application

```
## Plan Review: #2063 — Drilling Riser Adapter

Execution pack prepared at `docs/plans/claude-followup-2026-04-09/results/issue-2063-execution-pack.md`.

**Scope**: Add `adapter.py` to `digitalmodel/src/digitalmodel/drilling_riser/` that converts
worldenergydata CSV records (imperial) to SI calculation-ready dicts, following the #1859
`normalize_*_record` / `register_*` pattern. 6 TDD integration tests. No worldenergydata changes.

**Files**: 2 new (`adapter.py`, `test_adapter_integration.py`), 2 modified (`__init__.py`, `conftest.py`).

**Dependencies**: #1859 ✅ DONE. No blockers.

**Wave**: 1 (high-confidence batch alongside #2059 and #2056).

Requesting review before `status:plan-approved` label.
```

### For `status:plan-approved` label transition

```
## Plan Approved: #2063

Execution pack reviewed and approved. Implementation may proceed per the TDD task sequence
in the execution pack. Reminder:
- TDD first (write failing tests before adapter code)
- Commit inside `digitalmodel/` submodule, then update pointer in workspace-hub
- Post summary comment on this issue after implementation
- Cross-review required per workspace-hub policy
```

---

RECOMMENDATION: READY FOR PLAN-APPROVAL LABEL
