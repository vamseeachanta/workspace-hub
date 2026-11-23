# Execution Pack — Issue #2059

> feat(naval-arch): real vessel stability test cases from fleet data (Sleipnir, Thialf, Balder)

**Date**: 2026-04-09
**Source dossier**: `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md`
**Wave priority**: Wave 1, position 1 (per agent-team-followup-summary)
**Dependencies**: #1859 (fleet adapter) — DONE | #1850 (floating platform stability) — DONE

---

## 1. Executive Summary

Issue #2059 extends the existing naval architecture test suite with real-world vessel stability test cases for three Heerema semi-submersible crane vessels (Sleipnir, Thialf, Balder) using fleet data already loaded via the completed #1859 adapter. The overnight codebase audit confirmed that all production source modules (`ship_data.py`, `floating_platform_stability.py`, `curves_of_form.py`) are fully implemented and passing. The remaining work is **test-only**: adding a BALDER fixture, parametrized stability tests across all 3 named vessels, a CSV bulk-registration smoke test, and physical-reasonableness assertions on GZ curves — totaling approximately 80–120 lines of new test code in a single file. This is the smallest-delta, highest-confidence implementation candidate in the current batch.

---

## 2. Exact Scope Approved for Implementation

### 2.1 New test fixtures
- Add `BALDER_RECORD` dict fixture (152m × 76.8m × 25m, Heerema, 1978, DP2, 6300t crane) to `test_vessel_fleet_adapter.py`

### 2.2 New test classes / methods
- `TestCSVBulkRegistration` — loads all 17 records from `construction_vessels.csv`, calls `register_fleet_vessels()`, asserts count
- `TestRealVesselStability` — parametrized over SLEIPNIR, THIALF, BALDER with pytest IDs documenting assumed vs measured params:
  - `test_stability_produces_nontrivial_result` — registers vessel, estimates hydrostatics, computes GZ curve, runs `check_intact_stability()` for SEMISUB type
  - `test_gz_curve_physically_reasonable` — positive GZ at small angles, peak between 15–70°, area under curve is positive
  - `test_semisub_imo_criteria_evaluation` — StabilityResult contains `intact` bool and `gm_m > 0`
- Physical reasonableness bounds: GM ∈ [0.5, 50] m, max GZ angle ∈ [15°, 70°], GZ(30°) > 0, area(0–30) > 0

### 2.3 Documentation in tests
- Every test docstring labels parameters as MEASURED (dimensions from CSV, THIALF displacement 71,368 t) or ASSUMED (Cb=0.65 default, KG=0.6×T, Cw=0.72, Sleipnir/Balder displacement, wind params)
- Parametrize IDs: `sleipnir-assumed-Cb`, `thialf-measured-disp`, `balder-assumed-Cb`

### 2.4 Optional source enhancement (conditional)
- If GM values are clearly physically unreasonable with monohull defaults, add `vessel_subtype` parameter to `estimate_vessel_hydrostatics()` with semi-sub-specific defaults: Cb=0.50, Cw=0.55
- **Decision gate**: only implement if test results show monohull defaults produce GM outside [0.5, 50] m range

---

## 3. Explicit Out-of-Scope List

| Item | Reason |
|------|--------|
| Editing `floating_platform_stability.py` | Already complete per #1850 |
| Adding new vessel types beyond semi-submersibles | Issue scopes to Sleipnir, Thialf, Balder only |
| Modifying `construction_vessels.csv` data | Read-only data source; missing displacement is handled by estimation |
| Changing the `_SHIPS` registry architecture | Pre-existing test isolation bug (`test_register_multiple_vessels`) is a separate fix |
| Drilling rig stability tests | Separate issue (#2062) |
| Monohull stability tests | Not requested; issue focuses on semi-subs |
| Fixing the pre-existing test failure (`TestRegisterFleetVessels::test_register_multiple_vessels`) | Pre-existing isolation bug unrelated to #2059 scope |
| CI/CD or hook changes | No infrastructure changes needed |
| Documentation outside test files | No separate docs required |

---

## 4. TDD-First Task Sequence

### Phase 1: Write Failing Tests

| Step | Action | Expected State |
|------|--------|---------------|
| 1.1 | Add `BALDER_RECORD` fixture after `THIALF_RECORD` (~line 45) | New fixture, no tests using it yet |
| 1.2 | Add `TestCSVBulkRegistration::test_register_all_17_from_csv` | FAIL — test written, verifying CSV path resolution and count |
| 1.3 | Add parametrized `TestRealVesselStability` class with 4 test methods × 3 vessels = 12 test cases | FAIL — test bodies call stability pipeline, assert physical bounds |
| 1.4 | Run: `cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short` | Confirm new tests fail for the right reasons (not import errors) |

### Phase 2: Make Tests Pass

| Step | Action | Expected State |
|------|--------|---------------|
| 2.1 | Implement test bodies: register → estimate_hydrostatics → compute_gz_curve → check_intact_stability | Tests run through full pipeline |
| 2.2 | Evaluate GM values — if outside [0.5, 50] m for any vessel, add semi-sub Cb/Cw defaults to `ship_data.py` | Conditional source edit |
| 2.3 | Add docstrings with ASSUMED/MEASURED labels to every test method | Documentation complete |
| 2.4 | Run: `cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short` | All new tests PASS |

### Phase 3: Verify No Regressions

| Step | Action | Expected State |
|------|--------|---------------|
| 3.1 | Run full suite: `cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short` | All pass except pre-existing `test_register_multiple_vessels` failure |
| 3.2 | Quick REPL sanity check for Balder stability output | GM and GZ values printed, physically reasonable |
| 3.3 | Verify CSV path resolves correctly from test file location | Path exists, 17 records confirmed |

---

## 5. Exact Files Expected to Change

| File | Action | Lines Added (est.) | Risk |
|------|--------|--------------------|------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | EXTEND — add fixture + 2 new test classes | 80–120 | LOW — additive only, appended at end of file |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | POSSIBLE MINOR EDIT — semi-sub Cb/Cw defaults | 5–10 | LOW — conditional, backward-compatible parameter addition |

**Files that must NOT change:**
- `digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py`
- `digitalmodel/src/digitalmodel/naval_architecture/curves_of_form.py`
- `digitalmodel/src/digitalmodel/naval_architecture/hydrostatics.py`
- `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py`
- `worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv`

---

## 6. Git Contention Notes

| Concern | Risk Level | Detail |
|---------|-----------|--------|
| `test_vessel_fleet_adapter.py` concurrent edits | LOW | File is 399 lines; all changes are additive at end-of-file (new fixture after line 45, new classes after line 398). No modifications to existing lines. |
| `ship_data.py` optional edit | LOW | If needed, adds a single conditional branch inside `estimate_vessel_hydrostatics()`. Isolated change site. |
| Submodule `worldenergydata` | NONE | Read-only dependency. No writes. |
| Cross-issue conflicts | NONE | #2059 touches only naval_architecture tests. Wave 1 peer (#2063) works in `drilling_riser/` — zero overlap. Wave 1 peer (#2056) works in `.claude/hooks/` and `scripts/enforcement/` — zero overlap. |
| Branch strategy | N/A | Implement on feature branch `feat/2059-vessel-stability-tests`, single atomic commit preferred |

---

## 7. Self-Contained Claude Implementation Prompt

```
TASK: Implement #2059 — real vessel stability test cases from fleet data
BRANCH: feat/2059-vessel-stability-tests (create from main)
COMMIT STYLE: Single atomic commit: "feat(naval-arch): real vessel stability test cases for Sleipnir, Thialf, Balder (#2059)"

CONTEXT:
- Dependencies #1859 and #1850 are both complete and merged to main
- Source modules (fully implemented, DO NOT MODIFY unless Step 7 triggers):
  - digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
  - digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py
- Test file to extend:
  - digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py (399 lines)
- Data source (read-only):
  - worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv (17 records)

STEP 1 — READ existing code:
- Read test_vessel_fleet_adapter.py fully to understand existing fixtures and test patterns
- Read ship_data.py to understand register_fleet_vessels(), get_ship(), estimate_vessel_hydrostatics()
- Read floating_platform_stability.py to understand compute_gz_curve(), check_intact_stability(), PlatformType, STABILITY_CRITERIA

STEP 2 — ADD BALDER fixture (after THIALF_RECORD, ~line 45):
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

STEP 3 — WRITE FAILING TESTS (TDD: tests first, then make them pass):

3a. TestCSVBulkRegistration class:
  - test_register_all_17_from_csv: load CSV via csv.DictReader, call register_fleet_vessels(records), assert added + skipped == 17 and added >= 15
  - Use pathlib.Path(__file__).resolve().parents[3] / "worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv"

3b. TestRealVesselStability parametrized class:
  - Parametrize over (SLEIPNIR_RECORD, THIALF_RECORD, BALDER_RECORD) with IDs: "sleipnir-assumed-Cb", "thialf-measured-disp", "balder-assumed-Cb"
  - test_stability_produces_nontrivial_result:
    - register_fleet_vessels([record])
    - ship = get_ship(vessel_name)
    - hydro = estimate_vessel_hydrostatics(ship)
    - gm_m = hydro["gm_ft"] * 0.3048
    - gz_curve = compute_gz_curve(gm_m)
    - wind = compute_wind_heel(wind_pressure_kpa=0.5, projected_area_m2=5000, heeling_arm_m=15.0, displacement_t=hydro.get("displacement_t", 50000), gm_m=gm_m)
    - result = check_intact_stability("semisubmersible", gm_m, gz_curve, wind)
    - Assert: gm_m > 0, len(gz_curve) >= 10, isinstance(result.intact, bool)
  - test_gz_curve_physically_reasonable:
    - Assert: GM in [0.5, 50] m
    - Assert: max GZ occurs between 15° and 70°
    - Assert: GZ at 30° > 0
  - test_area_under_gz_positive:
    - compute_area_under_gz(gz_curve, 0, 30) > 0
  - test_assumed_vs_measured_documented:
    - This test simply verifies the parametrize IDs contain "assumed" or "measured" (meta-test for documentation compliance)

3c. Every test method MUST have a docstring labeling parameters:
  - MEASURED: LOA, BEAM, DRAFT (from CSV for all 3)
  - MEASURED: THIALF displacement (71,368 t)
  - ASSUMED: Sleipnir/Balder displacement (Cb=0.65 default)
  - ASSUMED: KG = 0.6 × draft, Cw = 0.72
  - ASSUMED: Wind params (0.5 kPa, 5000 m², 15m arm)

STEP 4 — RUN TESTS (expect failures):
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short

STEP 5 — IMPLEMENT test bodies to make them pass:
- Wire up the stability pipeline calls in each test
- Adjust physical bounds if initial runs show tighter ranges

STEP 6 — VERIFY:
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short
- All new tests must PASS
- Pre-existing test_register_multiple_vessels failure is expected and out of scope

STEP 7 — CONDITIONAL: If any vessel produces GM outside [0.5, 50] m:
- Add vessel_subtype parameter to estimate_vessel_hydrostatics() in ship_data.py
- If vessel_subtype == "semi_submersible": use Cb_default=0.50, Cw_default=0.55
- Re-run tests to confirm improvement
- Only do this if monohull defaults produce clearly wrong results

STEP 8 — COMMIT:
git add digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
# Only if Step 7 was triggered:
git add digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
git commit -m "feat(naval-arch): real vessel stability test cases for Sleipnir, Thialf, Balder (#2059)"

STEP 9 — UPDATE workspace-hub submodule pointer:
cd /mnt/local-analysis/workspace-hub
git add digitalmodel
git commit -m "chore(submodule): update digitalmodel for vessel stability tests (#2059)"

ACCEPTANCE CRITERIA (all must be true before marking done):
- AC-1: At least 3 real construction vessels (Sleipnir, Thialf, Balder) produce non-trivial StabilityResult
- AC-2: Semi-submersible vessels evaluated against SEMISUB IMO criteria (pass or fail with physically reasonable values)
- AC-3: Every test docstring documents ASSUMED vs MEASURED parameters
- AC-4: All new tests pass with uv run python -m pytest
- AC-5: No regressions in existing naval_architecture tests (except pre-existing isolation bug)

POST-IMPLEMENTATION:
- Post summary comment on GitHub issue #2059 with test results
- Run required cross-review per workspace-hub policy (minimum 2-provider review before merge)
- Do NOT modify any files outside the scope listed above
```

---

## 8. Approval Checklist

- [ ] Executive summary reviewed — scope is test-only with conditional minor source edit
- [ ] Dependencies confirmed complete: #1859 DONE, #1850 DONE
- [ ] Out-of-scope list reviewed — no feature creep risk
- [ ] TDD sequence is sound — tests written before implementation
- [ ] File change list is minimal and additive — no destructive edits
- [ ] Git contention risk is LOW — no overlap with Wave 1 peers (#2063, #2056)
- [ ] Implementation prompt is self-contained — can be dispatched to a fresh agent session
- [ ] Physical reasonableness bounds are appropriate for semi-submersible crane vessels
- [ ] Pre-existing test failure (`test_register_multiple_vessels`) excluded from scope
- [ ] Conditional source edit (Step 7) has clear trigger criteria

---

## 9. Suggested Issue Comment Text

### For `status:plan-review` label:

```markdown
**Plan review posted** — execution pack prepared at `docs/plans/claude-followup-2026-04-09/results/issue-2059-execution-pack.md`

**Summary**: Test-only implementation (~80-120 lines) adding real vessel stability cases for Sleipnir, Thialf, and Balder to `test_vessel_fleet_adapter.py`. All production source modules are already complete via #1859 and #1850. Conditional minor edit to `ship_data.py` only if monohull form coefficient defaults produce unreasonable GM values for semi-subs.

**Key decisions for review**:
1. Physical reasonableness bounds: GM ∈ [0.5, 50] m — appropriate for large semi-sub crane vessels?
2. Conditional Cb/Cw override: implement only if monohull defaults fail bounds check — agree?
3. Pre-existing `test_register_multiple_vessels` isolation bug is explicitly out of scope

Labeling `status:plan-review`. Please review and approve or request changes.
```

### For `status:plan-approved` transition:

```markdown
**Plan approved** — execution pack at `docs/plans/claude-followup-2026-04-09/results/issue-2059-execution-pack.md` is cleared for implementation.

Scope: TDD-first test extension for 3 real vessel stability cases. Branch: `feat/2059-vessel-stability-tests`. Single atomic commit.

Transitioning from `status:plan-review` → `status:plan-approved`.
```

---

RECOMMENDATION: READY FOR PLAN-APPROVAL LABEL
