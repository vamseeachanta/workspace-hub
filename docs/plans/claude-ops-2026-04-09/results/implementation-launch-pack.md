# Implementation Launch Pack — Batch 1

> Issues: #2059, #2063, #2056
> Date: 2026-04-09
> Source execution packs: `docs/plans/claude-followup-2026-04-09/results/issue-{2059,2063,2056}-execution-pack.md`
> Sequencing source: `docs/plans/2026-04-09-agent-team-followup-summary.md`

---

## 1. Recommended Execution Order

| Priority | Issue | Title | Confidence | Est. Delta |
|----------|-------|-------|------------|------------|
| 1 | #2059 | Real vessel stability test cases (Sleipnir, Thialf, Balder) | Highest — test-only, all source modules complete | ~80-120 lines |
| 2 | #2063 | Drilling riser adapter (imperial → SI) | High — clear adapter pattern, proven by #1859 | ~150-190 lines |
| 3 | #2056 | Session governance Phase 2: runtime hooks | High — all infrastructure exists, wiring-only | ~180 lines new + ~30 modified |

Rationale: #2059 is the smallest delta and pure test code — fastest to validate. #2063 adds production code but follows an established pattern. #2056 touches the most files and includes `.claude/settings.json` (highest-contention file in repo), so it benefits from running last if sequential.

---

## 2. Parallel vs. Sequential: PARALLEL (3 concurrent agents)

### Decision: Run all three in parallel

**Why parallel works:**
- Zero file overlap across all three issues (verified below)
- Independent test suites — no shared test infrastructure
- Independent dependencies — all prerequisites are already merged to main
- Each produces a single atomic commit on its own feature branch

**The one coordination constraint:**
- #2059 and #2063 both commit inside the `digitalmodel/` submodule. After both complete, their submodule pointer updates in workspace-hub must be serialized (second agent rebases onto first agent's pointer update). This is a post-implementation merge concern, not an implementation blocker.

**Risk if sequential:** Three sequential implementations would take ~3x wall-clock time with no safety benefit, since there is no shared state.

---

## 3. Non-Overlapping Write Boundaries

### #2059 — Naval Architecture Tests
| File | Action |
|------|--------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | EXTEND (append fixture + 2 test classes) |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | CONDITIONAL minor edit (semi-sub defaults, only if GM bounds fail) |

### #2063 — Drilling Riser Adapter
| File | Action |
|------|--------|
| `digitalmodel/src/digitalmodel/drilling_riser/adapter.py` | CREATE (new module) |
| `digitalmodel/tests/drilling_riser/test_adapter_integration.py` | CREATE (new test file) |
| `digitalmodel/src/digitalmodel/drilling_riser/__init__.py` | MODIFY (add 3 imports) |
| `digitalmodel/tests/drilling_riser/conftest.py` | MODIFY (add CSV fixture if needed) |

### #2056 — Governance Hooks
| File | Action |
|------|--------|
| `.claude/hooks/tool-call-ceiling.sh` | MODIFY (threshold 500→200, add JSON output) |
| `.claude/hooks/error-loop-breaker.sh` | CREATE (new hook) |
| `.claude/settings.json` | MODIFY (2 env vars + 1 PostToolUse entry) |
| `scripts/enforcement/require-review-on-push.sh` | MODIFY (strict default) |
| `scripts/workflow/governance-checkpoints.yaml` | MODIFY (enforced: true) |
| `docs/governance/SESSION-GOVERNANCE.md` | MODIFY (mark Phase 2b complete) |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | MODIFY (update default) |
| `tests/hooks/test_tool_call_ceiling.py` | CREATE (new test file) |
| `tests/hooks/test_error_loop_breaker.py` | CREATE (new test file) |
| `scripts/enforcement/tests/test_require_review_on_push.sh` | EXTEND (add strict-default tests) |

### Overlap Matrix

| | #2059 files | #2063 files | #2056 files |
|---|---|---|---|
| **#2059** | — | NONE | NONE |
| **#2063** | NONE | — | NONE |
| **#2056** | NONE | NONE | — |

**Verdict: Zero file overlap. Safe for full parallel execution.**

---

## 4. Self-Contained Claude Prompts

### Prompt A — Issue #2059

```
TASK: Implement #2059 — real vessel stability test cases from fleet data
BRANCH: feat/2059-vessel-stability-tests (create from main)
COMMIT: "feat(naval-arch): real vessel stability test cases for Sleipnir, Thialf, Balder (#2059)"

PREREQUISITES: Verify #2059 has label status:plan-approved. Run git pull.

CONTEXT:
- Dependencies #1859 (fleet adapter) and #1850 (floating platform stability) are DONE
- Source modules are fully implemented — DO NOT MODIFY unless Step 7 triggers
- Test file to extend: digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py (399 lines)
- Data source (read-only): worldenergydata/data/modules/vessel_fleet/curated/construction_vessels.csv

STEP 1 — READ existing code:
- Read test_vessel_fleet_adapter.py (understand existing fixtures and patterns)
- Read ship_data.py (register_fleet_vessels, get_ship, estimate_vessel_hydrostatics)
- Read floating_platform_stability.py (compute_gz_curve, check_intact_stability, PlatformType)

STEP 2 — ADD BALDER fixture after THIALF_RECORD (~line 45):
BALDER_RECORD = {
    "VESSEL_NAME": "BALDER", "VESSEL_CATEGORY": "construction",
    "VESSEL_TYPE": "crane_vessel", "VESSEL_SUBTYPE": "semi_submersible",
    "OWNER": "Heerema Marine Contractors", "LOA_M": 152.0, "BEAM_M": 76.8,
    "DRAFT_M": 25.0, "DISPLACEMENT_TONNES": None, "GROSS_TONNAGE": None,
    "DP_CLASS": 2, "YEAR_BUILT": 1978, "MAIN_CRANE_CAPACITY_T": 6300.0,
}

STEP 3 — WRITE FAILING TESTS (TDD: tests before implementation):

3a. TestCSVBulkRegistration:
  - test_register_all_17_from_csv: load CSV, call register_fleet_vessels(records),
    assert added + skipped == 17, added >= 15

3b. TestRealVesselStability parametrized over (SLEIPNIR, THIALF, BALDER):
  - Parametrize IDs: "sleipnir-assumed-Cb", "thialf-measured-disp", "balder-assumed-Cb"
  - test_stability_produces_nontrivial_result: register → hydrostatics → GZ curve →
    check_intact_stability. Assert GM > 0, len(gz_curve) >= 10, result.intact is bool
  - test_gz_curve_physically_reasonable: GM in [0.5, 50] m, max GZ at 15-70 deg, GZ(30) > 0
  - test_area_under_gz_positive: area(0-30) > 0
  - test_assumed_vs_measured_documented: verify parametrize IDs contain "assumed" or "measured"
  - Every docstring labels params as MEASURED or ASSUMED

STEP 4 — RUN (expect failures):
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short

STEP 5 — IMPLEMENT test bodies to make them pass

STEP 6 — VERIFY:
cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v --tb=short
cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v --tb=short
(pre-existing test_register_multiple_vessels failure is expected and out of scope)

STEP 7 — CONDITIONAL: If any vessel GM outside [0.5, 50] m, add semi-sub defaults
(Cb=0.50, Cw=0.55) to estimate_vessel_hydrostatics() in ship_data.py. Only if needed.

STEP 8 — COMMIT:
git add digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
# Only if Step 7 triggered: git add digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
git commit -m "feat(naval-arch): real vessel stability test cases for Sleipnir, Thialf, Balder (#2059)"

STEP 9 — Post summary comment on GitHub issue #2059 with test results.

ACCEPTANCE CRITERIA:
- AC-1: 3 real vessels (Sleipnir, Thialf, Balder) produce non-trivial StabilityResult
- AC-2: Semi-subs evaluated against SEMISUB IMO criteria with physically reasonable values
- AC-3: Every test docstring documents ASSUMED vs MEASURED parameters
- AC-4: All new tests pass
- AC-5: No regressions in existing naval_architecture tests
```

---

### Prompt B — Issue #2063

```
TASK: Implement #2063 — wire drilling riser components into mooring/riser analysis
BRANCH: feat/2063-drilling-riser-adapter (create from main)
COMMIT (digitalmodel): "feat(drilling-riser): add worldenergydata adapter for riser components (#2063)"
COMMIT (workspace-hub): "chore(submodule): update digitalmodel for drilling riser adapter (#2063)"

PREREQUISITES: Verify #2063 has label status:plan-approved. Run git pull.

CONTEXT:
- Source data: worldenergydata/data/modules/vessel_fleet/curated/drilling_riser_components.csv
  (36 records, imperial units: inches, feet, kips, psi)
- Calculation module: digitalmodel/src/digitalmodel/drilling_riser/ (12 pure functions, 37+ tests)
- Pattern reference: digitalmodel/src/digitalmodel/naval_architecture/ship_data.py
  (normalize_fleet_record / register_fleet_vessels — follow this pattern exactly)
- Gap: NO adapter connects the CSV data to the calculation module. You are building that bridge.

STEP 1 — WRITE FAILING TESTS:
Create digitalmodel/tests/drilling_riser/test_adapter_integration.py with 6 tests:

T1: test_normalize_riser_joint_21in_bare
    Input: {COMPONENT_ID: "RJ-21-75-BARE", OD_IN: 21.0, ID_IN: 19.5, WALL_THICKNESS_IN: 0.75,
            LENGTH_FT: 75.0, WEIGHT_AIR_KIPS: 22.5, WEIGHT_WATER_KIPS: 3.8,
            GRADE: "X-80", PRESSURE_RATING_PSI: 5000.0}
    Assert: od_mm ≈ 533.4, submerged_weight_kn ≈ 16.903, length_m ≈ 22.86, pressure_mpa ≈ 34.47

T2: test_normalize_bop_record
    Input: {COMPONENT_ID: "BOP-SUB-18.75-15K", WEIGHT_AIR_KIPS: 400.0,
            WEIGHT_WATER_KIPS: 340.0, BORE_SIZE_IN: 18.75, HEIGHT_FT: 35.0,
            PRESSURE_RATING_PSI: 15000.0}
    Assert: submerged_weight_kn ≈ 1512.39, height_m ≈ 10.668

T3: test_normalize_returns_none_for_missing_id — returns None when COMPONENT_ID absent
T4: test_register_riser_components_all_36 — added + skipped == 36, added >= 33
T5: test_riser_string_weight_20_bare_joints — 20 joints × 3.8 × 4.44822 ≈ 338.06 kN
T6: test_tool_passage_real_specs — annular_clearance_mm(19.5*25.4, 12.25*25.4) ≈ 92.075

Run: cd digitalmodel && uv run pytest tests/drilling_riser/test_adapter_integration.py -v
Confirm: all 6 FAIL.

STEP 2 — IMPLEMENT ADAPTER:
Create digitalmodel/src/digitalmodel/drilling_riser/adapter.py:
    _KIPS_TO_KN = 4.44822
    _IN_TO_MM = 25.4
    _FT_TO_M = 0.3048
    _PSI_TO_MPA = 0.00689476

    normalize_riser_component_record(record) -> Optional[dict]
    register_riser_components(records, *, registry=None) -> tuple[int, int]
    compute_riser_string_weight_kn(components) -> float

STEP 3 — UPDATE __init__.py: add 3 imports + extend __all__
STEP 4 — UPDATE conftest.py if shared CSV fixture needed

STEP 5 — RUN ALL drilling_riser tests:
cd digitalmodel && uv run pytest tests/drilling_riser/ -v
All 6 new + ~37 existing must pass. Zero regressions.

STEP 6 — COMMIT:
cd digitalmodel
git add src/digitalmodel/drilling_riser/adapter.py \
        tests/drilling_riser/test_adapter_integration.py \
        src/digitalmodel/drilling_riser/__init__.py \
        tests/drilling_riser/conftest.py
git commit -m "feat(drilling-riser): add worldenergydata adapter for riser components (#2063)"

Then update submodule pointer:
cd /mnt/local-analysis/workspace-hub
git add digitalmodel
git commit -m "chore(submodule): update digitalmodel for drilling riser adapter (#2063)"

STEP 7 — Post summary comment on GitHub issue #2063.

CONSTRAINTS:
- Do NOT modify any worldenergydata files
- Do NOT modify existing drilling_riser calculation functions
- Do NOT use pint — use plain multiplication constants
- Do NOT wire to legacy typical_riser_stack_up_calculations.py
```

---

### Prompt C — Issue #2056

```
TASK: Implement #2056 — Session governance Phase 2: wire runtime enforcement into hooks
BRANCH: feat/2056-governance-phase2-hooks (create from main)
COMMIT: "feat(governance): wire Phase 2 runtime enforcement into hooks (#2056)"

PREREQUISITES:
- Verify #2056 has label status:plan-approved
- git pull && git log --oneline -5 (confirm latest main)
- git log --since="6 hours ago" -- .claude/settings.json (check for in-flight edits)

STEP 1 — RED: Write failing tests FIRST

1a. Create tests/hooks/test_tool_call_ceiling.py:
   - Test default ceiling is 200
   - Test at 200 calls: hook outputs additionalContext JSON with progress summary
   - Test at 160 calls (80%): hook outputs warning context
   - Test below 160: hook exits 0 with no stdout
   - Test TOOL_CALL_CEILING env var overrides threshold

1b. Create tests/hooks/test_error_loop_breaker.py:
   - Test error hashing: strip timestamps, absolute paths, line numbers, then md5sum
   - Test 3 consecutive identical errors → STOP verdict (exit 2)
   - Test different error resets counter to 1
   - Test non-error resets counter to 0
   - Test state file at /tmp/claude-error-loop-${SESSION_ID:-default}.json
   - Test hook outputs additionalContext JSON on STOP

1c. Extend scripts/enforcement/tests/test_require_review_on_push.sh:
   - Test default mode blocks push (exit 1)
   - Test REVIEW_GATE_STRICT=0 overrides to warn (exit 0)
   - Test SKIP_REVIEW_GATE=1 logs audit entry + emits stderr warning

1d. Run all — confirm FAIL:
   uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v
   uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v
   bash scripts/enforcement/tests/test_require_review_on_push.sh

STEP 2 — GREEN: Implement

2a. .claude/hooks/tool-call-ceiling.sh:
   - Change CEILING="${TOOL_CALL_CEILING:-500}" → CEILING="${TOOL_CALL_CEILING:-200}"
   - Add JSON stdout with additionalContext at STOP (>=200) and PAUSE (>=160)
   - Integrate session_governor.py --check-limits --tool-calls $COUNT

2b. .claude/hooks/error-loop-breaker.sh (new):
   - PostToolUse hook for Bash tool
   - Read stdin JSON, extract output and exit code
   - Hash error messages (strip timestamps, paths, line numbers) via md5sum
   - Track state in /tmp/claude-error-loop-${SESSION_ID:-default}.json
   - 3 consecutive identical → call session_governor.py --check-limits --consecutive-errors N
   - On STOP: output additionalContext JSON; on success: reset counter

2c. .claude/settings.json:
   - Add env: "TOOL_CALL_CEILING": "200", "REVIEW_GATE_STRICT": "1"
   - Add PostToolUse entry for error-loop-breaker.sh (matcher: Bash, timeout: 5)

2d. scripts/enforcement/require-review-on-push.sh:
   - Change "${REVIEW_GATE_STRICT:-}" → "${REVIEW_GATE_STRICT:-1}"
   - Add stderr warning in bypass path

2e. scripts/workflow/governance-checkpoints.yaml:
   - enforced: false → enforced: true

2f. Documentation:
   - docs/governance/SESSION-GOVERNANCE.md: mark Phase 2b complete
   - docs/standards/REVIEW_GATE_BYPASS_POLICY.md: update default to strict

STEP 3 — VERIFY:
uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v
uv run --no-project python -m pytest tests/hooks/test_tool_call_ceiling.py -v
uv run --no-project python -m pytest tests/hooks/test_error_loop_breaker.py -v
bash scripts/enforcement/tests/test_require_review_on_push.sh
grep 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh  # must show 200
grep 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh  # must show 1
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 200  # exit 2
uv run scripts/workflow/session_governor.py --check-limits --tool-calls 150  # exit 0
uv run scripts/workflow/session_governor.py --check-limits --consecutive-errors 3  # exit 2
test -f .claude/hooks/error-loop-breaker.sh && echo "PASS"

STEP 4 — COMMIT:
git add .claude/hooks/tool-call-ceiling.sh .claude/hooks/error-loop-breaker.sh \
  .claude/settings.json scripts/enforcement/require-review-on-push.sh \
  scripts/workflow/governance-checkpoints.yaml \
  docs/governance/SESSION-GOVERNANCE.md docs/standards/REVIEW_GATE_BYPASS_POLICY.md \
  tests/hooks/test_tool_call_ceiling.py tests/hooks/test_error_loop_breaker.py \
  scripts/enforcement/tests/test_require_review_on_push.sh
git commit -m "feat(governance): wire Phase 2 runtime enforcement into hooks (#2056)"

STEP 5 — Post summary comment on GitHub issue #2056.

ACCEPTANCE CRITERIA:
- Tool-call ceiling fires at 200 (not 500) with additionalContext progress summary
- Error-loop-breaker detects 3x identical errors and injects hard-stop context
- Pre-push review gate defaults to strict (exit 1)
- SKIP_REVIEW_GATE=1 emits visible stderr warning
- All new + existing governance tests pass
- governance-checkpoints.yaml marks pre-push-review as enforced: true
```

---

## 5. Post-Implementation Verification Checklist

### Per-Issue Checks

#### #2059 — Vessel Stability Tests
- [ ] `cd digitalmodel && uv run python -m pytest tests/naval_architecture/test_vessel_fleet_adapter.py -v` — all new tests PASS
- [ ] `cd digitalmodel && uv run python -m pytest tests/naval_architecture/ -v` — no regressions (except pre-existing isolation bug)
- [ ] BALDER_RECORD fixture present with correct dimensions (152m x 76.8m x 25m)
- [ ] All 3 vessels produce GM in [0.5, 50] m range
- [ ] Every test docstring labels ASSUMED vs MEASURED parameters
- [ ] Summary comment posted on GitHub issue #2059

#### #2063 — Drilling Riser Adapter
- [ ] `cd digitalmodel && uv run pytest tests/drilling_riser/ -v` — all 6 new + ~37 existing pass
- [ ] `uv run python -c "from digitalmodel.drilling_riser.adapter import normalize_riser_component_record; print('OK')"` — import works
- [ ] Unit conversions verified: 21 in → 533.4 mm, 75 ft → 22.86 m, 3.8 kips → 16.903 kN
- [ ] No files modified in worldenergydata/
- [ ] Submodule pointer updated in workspace-hub
- [ ] Summary comment posted on GitHub issue #2063

#### #2056 — Governance Hooks
- [ ] `uv run --no-project python -m pytest tests/work-queue/test_session_governor.py -v` — existing pass
- [ ] `uv run --no-project python -m pytest tests/hooks/ -v` — new tests pass
- [ ] `bash scripts/enforcement/tests/test_require_review_on_push.sh` — strict default confirmed
- [ ] `grep 'TOOL_CALL_CEILING:-' .claude/hooks/tool-call-ceiling.sh` returns `200`
- [ ] `grep 'REVIEW_GATE_STRICT:-' scripts/enforcement/require-review-on-push.sh` returns `1`
- [ ] Error-loop-breaker hook exists and is registered in settings.json
- [ ] Governor returns exit 2 at 200 tool calls and exit 2 at 3 consecutive errors
- [ ] Summary comment posted on GitHub issue #2056

### Cross-Issue Checks
- [ ] No unintended file overlap between the three commits (verify with `git diff --name-only` per branch)
- [ ] digitalmodel submodule pointer includes both #2059 and #2063 changes (if both landed)
- [ ] `git log --oneline -5` shows 3 clean atomic commits (+ submodule pointer updates)
- [ ] All three GitHub issues have summary comments posted

---

## 6. Cross-Review Routing Recommendation

Per workspace-hub cross-review policy (2-provider minimum):

| Issue | Primary Reviewer | Secondary Reviewer | Rationale |
|-------|-----------------|-------------------|-----------|
| #2059 | Codex (`/codex:rescue` or `/gsd:review --codex`) | Gemini CLI | Domain-specific naval architecture — needs computation verification. Codex for numerical sanity, Gemini for pattern adherence. |
| #2063 | Codex | Gemini CLI | Unit conversion accuracy is critical — Codex excels at arithmetic verification. Gemini confirms adapter pattern consistency with ship_data.py. |
| #2056 | Gemini CLI | Codex | Hook wiring and JSON protocol — Gemini for shell script review and settings.json structural integrity. Codex for governor integration correctness. |

**Review order**: Review each issue independently after its implementation completes. Do not batch reviews — review as each agent finishes to unblock merging.

**Review command**: `/gsd:review --codex` per issue, then a second provider review via Gemini CLI or Hermes routing.

**Merge order**: #2059 first (smallest, test-only), then #2063 (update submodule pointer after #2059's pointer), then #2056 (governance last — avoids stricter hooks affecting the other two implementations).

---

RECOMMENDATION: READY TO LAUNCH AFTER LABELS ARE APPROVED
