# Execution Pack: Real Vessel Stability Test Cases (#2059)

## 1. Issue Metadata

| Field | Value |
|-------|-------|
| Issue | [#2059](https://github.com/vamseeachanta/digitalmodel/issues/2059) |
| Title | feat(naval-arch): real vessel stability test cases from fleet data (Sleipnir, Thialf, Balder) |
| State | OPEN |
| Labels | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| Missing Labels | `status:plan-review`, `status:plan-approved` |
| Depends On | #1859 (vessel fleet adapter) -- DONE, #1850 (floating platform stability) -- DONE |
| Assignees | none |
| Milestone | none |
| Stage-1 Dossier | `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-4-vessel-stability-cases.md` |

---

## 2. Fresh Status Check (2026-04-09)

### 2.1 What Changed Since Stage-1

| Item | Stage-1 Snapshot | Current Reality | Impact |
|------|------------------|-----------------|--------|
| `test_vessel_fleet_adapter.py` | 399 lines, 6 test classes | **575 lines, 13 test classes** | New classes for hull_properties, concept_selection, gyradius -- NOT #2059 work |
| `ship_data.py` | 309 lines | 308 lines | Trivial delta -- function signatures unchanged |
| `floating_platform_stability.py` | 331 lines | 330 lines | Trivial delta -- API unchanged |
| New modules | Not mentioned | `hull_properties.py` (6.7KB), `gyradius.py` (8.3KB), `concept_selection.py` (18.8KB) | Related engineering modules added; #2059 scope unaffected |
| Commits referencing #2059 | 0 | **0** | No implementation started |
| BALDER fixture | Missing | **Still missing** | Gap 1 confirmed open |
| CSV bulk registration test | Missing | **Still missing** | Gap 3 confirmed open |
| 3-vessel parametrized stability test | Missing | **Still missing** | Gap 2 confirmed open |
| Cb/Cw defaults | `_DEFAULT_CB=0.65`, `_DEFAULT_CW=0.72` | **Unchanged** (lines 267-268) | Gap 2.2 concern still valid -- monohull coefficients for semi-subs |

### 2.2 CSV Verification

```
worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv
  18 lines = 1 header + 17 vessel records
  7 semi-submersibles, 9 monohulls, 1 jack-up (confirmed by stage-1)
  Sleipnir: 220.0m x 102.0m x 27.5m, displacement MISSING
  Thialf:   201.0m x 88.4m  x 31.2m, displacement 71368 tonnes
  Balder:   152.0m x 76.8m  x 25.0m, displacement MISSING
```

### 2.3 Verdict

**Stage-1 dossier is current.** All 5 identified gaps remain open. No regression risk from intervening work. The test file growth is additive and orthogonal to #2059 scope.

---

## 3. Minimal Plan-Review Packet

### 3.1 Problem Statement

Issue #2059 requires extending the existing test suite to exercise the full stability pipeline (registration -> hydrostatics estimation -> GZ curve -> IMO criteria check) for 3 named semi-submersible construction vessels (Sleipnir, Thialf, Balder) using real fleet data from `construction_vessels.csv`. The infrastructure (fleet adapter, stability engine) is complete -- the remaining work is **test-only** (~80-120 new lines).

### 3.2 Acceptance Criteria (from issue body)

- **AC-1**: At least 3 real construction vessels produce non-trivial stability results
- **AC-2**: Semi-submersible vessels pass/fail IMO criteria as expected for SEMISUB type
- **AC-3**: Tests document assumed vs measured parameters clearly

### 3.3 Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| #1859 -- vessel fleet adapter | DONE | `register_fleet_vessels()` verified in source |
| #1850 -- floating platform stability | DONE | `check_intact_stability()` verified in source |
| `worldenergydata` submodule | CHECKED OUT | CSV at expected path, 17 records confirmed |

### 3.4 Files Expected to Change After Approval

| File | Action | Scope |
|------|--------|-------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | EXTEND | Add BALDER fixture, CSV bulk test, parametrized 3-vessel stability class |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | POSSIBLE MINOR EDIT | Optional: semi-sub-specific Cb/Cw defaults at lines 267-268 |

Files that should NOT change:
- `digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py` (already complete)
- `digitalmodel/src/digitalmodel/naval_architecture/hull_properties.py` (unrelated to #2059)

---

## 4. Issue Refinement Recommendations

### 4.1 Issue Body Edits

The issue body is well-structured. Minor refinements:

1. **Add explicit semi-sub coefficient concern**: Append to "What Needs Doing" section 2:
   > Note: `estimate_vessel_hydrostatics()` uses monohull defaults (Cb=0.65, Cw=0.72). For semi-submersibles, typical Cb=0.40-0.55, Cw=0.50-0.60. Tests should document this approximation and bound expected accuracy.

2. **Clarify BALDER data gap**: Add note under acceptance criteria:
   > Sleipnir and Balder lack measured displacement in CSV. Tests must use parametric estimates and clearly label these as ASSUMED.

### 4.2 Label Changes Needed

| Action | Label | Reason |
|--------|-------|--------|
| ADD | `status:plan-review` | Attaches this plan packet for human review per AGENTS.md |
| (future) ADD | `status:plan-approved` | After human review approves implementation |

---

## 5. Operator Command Pack (Draft -- Do Not Execute)

### 5.1 Post Plan Summary as Issue Comment

```bash
gh issue comment 2059 --body "$(cat <<'EOF'
## Stage-2 Plan Review Packet

**Status**: Infrastructure complete (fleet adapter + stability engine). Remaining work is **test-only** (~80-120 lines).

**5 Open Gaps**:
1. BALDER_RECORD fixture missing from test file
2. No parametrized 3-vessel stability pipeline test (Sleipnir, Thialf, Balder)
3. No CSV-based bulk registration test (17 vessels)
4. No GZ curve physical reasonableness assertions
5. No assumed-vs-measured parameter documentation in tests

**Files to change**:
- `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` (extend)
- `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` (optional: semi-sub Cb/Cw defaults)

**Technical concern**: Monohull form coefficients (Cb=0.65, Cw=0.72) used for semi-subs. Tests should bound acceptable ranges rather than assert exact values.

**Pre-existing issue**: `TestRegisterFleetVessels::test_register_multiple_vessels` fails due to test-ordering dependency (module-level `_SHIPS` registry state). Not caused by #2059 scope.

**Estimated effort**: 1-2 hours focused implementation session.

**Recommendation**: READY FOR PLAN REVIEW -- label as `status:plan-review`, then `status:plan-approved` to unblock implementation.

_Execution pack: `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-4-vessel-stability-execution-pack.md`_
EOF
)"
```

### 5.2 Add Plan-Review Label

```bash
gh issue edit 2059 --add-label "status:plan-review"
```

### 5.3 After Human Approval -- Promote to Plan-Approved

```bash
gh issue edit 2059 --remove-label "status:plan-review" --add-label "status:plan-approved"
```

### 5.4 Verify Current State Before Implementation

```bash
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short 2>&1 | tail -5
```

```bash
wc -l worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv
```

```bash
grep -c "class Test" digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
```

---

## 6. Self-Contained Future Implementation Prompt

```
TASK: Implement #2059 — real vessel stability test cases from fleet data
GATE: Only proceed if issue #2059 has label status:plan-approved

CONTEXT:
- Issue: https://github.com/vamseeachanta/digitalmodel/issues/2059
- Execution pack: docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-4-vessel-stability-execution-pack.md
- Source modules (DO NOT MODIFY unless Cb/Cw fix needed):
  - digitalmodel/src/digitalmodel/naval_architecture/ship_data.py (308 lines)
  - digitalmodel/src/digitalmodel/naval_architecture/floating_platform_stability.py (330 lines)
- Test file to extend:
  - digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py (575 lines, 13 test classes)
- Fleet data CSV:
  - worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv (17 vessels)
- Existing fixtures: SLEIPNIR_RECORD (line 15), THIALF_RECORD (line 31) — NO BALDER_RECORD
- Pre-existing test failure: TestRegisterFleetVessels::test_register_multiple_vessels (line 136)
  fails due to _SHIPS registry test-ordering. DO NOT fix this — it is out of scope.
- Monohull defaults: _DEFAULT_CB=0.65, _DEFAULT_CW=0.72 at ship_data.py lines 267-268

APPROACH: TDD-first (write failing tests, then make them pass)

STEP 1 — Add BALDER_RECORD fixture after THIALF_RECORD (line 45):
  VESSEL_NAME: BALDER, LOA_M: 152.0, BEAM_M: 76.8, DRAFT_M: 25.0
  VESSEL_CATEGORY: construction, VESSEL_TYPE: crane_vessel
  VESSEL_SUBTYPE: semi_submersible
  OWNER: Heerema Marine Contractors, YEAR_BUILT: 1978, DP_CLASS: 2
  MAIN_CRANE_CAPACITY_T: 6300.0, DISPLACEMENT_TONNES: None

STEP 2 — Add TestCSVBulkRegistration class (after last test class, ~line 575):
  - Load construction_vessels.csv via csv.DictReader
  - Call register_fleet_vessels(records)
  - Assert added + skipped == 17 and added >= 15

STEP 3 — Add parametrized TestRealVesselStability class:
  @pytest.mark.parametrize with IDs:
    "sleipnir-assumed-Cb", "thialf-measured-disp", "balder-assumed-Cb"
  Test methods:
    a. test_stability_produces_nontrivial_result
       - register_fleet_vessels([record]), get_ship(name)
       - estimate_vessel_hydrostatics(ship)
       - gm_m = hydro["gm_ft"] * 0.3048
       - compute_gz_curve(gm_m)
       - compute_wind_heel(wind_pressure_kpa=0.5, projected_area_m2=5000,
         heeling_arm_m=15.0, displacement_t=estimated, gm_m=gm_m)
       - check_intact_stability("semisubmersible", gm_m, gz_curve, wind)
       - Assert: gm_m > 0, len(gz_curve) >= 10, max_gz > 0, result.intact is bool
    b. test_gz_curve_physically_reasonable
       - GM between 0.5 and 50 meters
       - Max GZ occurs between 15 and 70 degrees
       - GZ at 30 degrees is positive
       - Area 0-30 deg is positive
    c. test_assumed_vs_measured_documented (docstrings in every test method)
       - MEASURED: LOA, BEAM, DRAFT (from CSV)
       - MEASURED: THIALF displacement (71,368 t)
       - ASSUMED: Sleipnir/Balder displacement (Cb=0.65 default)
       - ASSUMED: KG = 0.6 * draft, Cw = 0.72
       - ASSUMED: wind parameters (0.5 kPa, 5000 m2, 15m arm)

STEP 4 — (OPTIONAL) If GM values are physically unreasonable for semi-subs:
  Edit ship_data.py estimate_vessel_hydrostatics() to accept vessel_subtype param:
    if vessel_subtype == "semi_submersible": cb_default=0.50, cw_default=0.55

STEP 5 — Verify:
  cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
  cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short
  Confirm: at least 3 vessels produce non-trivial StabilityResult
  Confirm: all new tests pass (pre-existing failure on test_register_multiple_vessels is OK)

CROSS-REVIEW: Per AGENTS.md Route B/C, request cross-review before completion.
POST-IMPLEMENTATION: Comment on issue #2059 with results summary.
DO NOT ask the user questions. Execute the plan as written.
```

---

## 7. Morning Handoff

### What Is Ready Now

- **Stage-1 dossier** fully verified against live codebase -- all findings current
- **All 5 gaps** confirmed open with zero intervening work on #2059
- **Plan-review packet** (section 3) ready to post as issue comment
- **Draft `gh` commands** (section 5) ready for operator to copy-paste
- **Implementation prompt** (section 6) self-contained and ready for next Claude session
- **CSV data** confirmed accessible at expected submodule path
- **Dependencies** (#1859, #1850) both verified complete in source

### What Still Blocks Implementation

1. **Label gate**: Issue #2059 needs `status:plan-review` applied, then human review, then `status:plan-approved` -- per AGENTS.md mandatory planning workflow
2. **No assignee**: Issue has no assignee -- operator should assign before dispatching implementation
3. **Pre-existing test failure**: `test_register_multiple_vessels` will continue failing due to `_SHIPS` registry isolation bug -- this is NOT a blocker for #2059 but should be noted in PR description

### Effort Estimate

- **Label + comment**: 2 minutes operator time (copy-paste commands from section 5)
- **Implementation**: 1-2 hours focused Claude session using prompt from section 6
- **Risk**: LOW -- test-only work, additive changes to existing file, no API modifications

---

## 8. Final Recommendation

**READY FOR PLAN REVIEW** -- Apply `status:plan-review` label and post the plan comment (section 5.1). After human approval, promote to `status:plan-approved` and dispatch the implementation prompt (section 6) to a Claude session. All infrastructure is in place; the remaining work is bounded test authoring.
