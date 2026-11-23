# WRK-1362 Plan: Chute Drag Force — Single and Dual Chute Assessment

## Context

Child of WRK-5082 (parachute frame force calculation). GT1R R35 (3,600 lbs) needs drag force at 200/250 MPH for frame design. Code and 25 tests were already written (uncommitted) but bypassed the staged workflow. This plan validates, fixes gaps, and completes the work properly.

## Current State

**Uncommitted work (passing 25/25 tests):**
- `chute_assessment.py` (232 lines) — dual chute, Stroud sizing, aero lift, traction, load case orchestrator
- `test_chute_assessment.py` (309 lines) — 25 tests across 5 classes
- `stroud-sizing-chart.py` — generates PNG visualization

## Issues to Fix

| # | Issue | Impact |
|---|-------|--------|
| A | `chute_assessment.py` at 232 lines (limit: 200) | Coding style violation |
| B | `test_chute_assessment.py` at 309 lines (limit: 200) | Coding style violation |
| C | No YAML export for downstream consumers (WRK-1363/1364/1365) | Missing interface contract |
| D | Hand-calc tests use absolute tolerance, not explicit 1% | AC6 not auditable |
| E | `__init__.py` doesn't export new symbols | Import usability |

## Implementation Steps

### Step 1: Split `chute_assessment.py` → `stroud_sizing.py` + `chute_assessment.py`
- Extract: `StroudRecommendation`, lookup tables, `recommend_stroud_chute()`, constants → `stroud_sizing.py` (~55 lines)
- Keep: dual chute, aero lift, traction, load cases, add YAML export → `chute_assessment.py` (~185 lines)

### Step 2: Split `test_chute_assessment.py` → `test_stroud_sizing.py` + `test_chute_assessment.py`
- Extract: `TestStroudRecommendation` (7 tests) → `test_stroud_sizing.py` (~90 lines)
- Keep: remaining 18 tests → `test_chute_assessment.py` (~195 lines)

### Step 3: Add `export_results_yaml()`
Output YAML with structure: `wrk_ref`, `vehicle_weight_lbs`, `load_cases[]`, `governing_case_id`, `governing_force_lbs`. This is the contract for WRK-1363/1364/1365.

### Step 4: Add explicit 1% tolerance test
Assert `abs(actual - expected) / expected < 0.01` for governing case.

### Step 5: Update `__init__.py` exports

### Step 6: Run all parachute tests (expect 100+ pass)

### Step 7: Commit in digitalmodel submodule, update hub pointer, push

## Files Changed

| File | Action | Est. Lines |
|------|--------|-----------|
| `src/.../parachute/stroud_sizing.py` | NEW | ~55 |
| `src/.../parachute/chute_assessment.py` | MODIFY | ~185 |
| `src/.../parachute/__init__.py` | MODIFY | ~12 |
| `tests/.../parachute/test_stroud_sizing.py` | NEW | ~90 |
| `tests/.../parachute/test_chute_assessment.py` | MODIFY | ~195 |

## Verification

1. All 25 existing tests pass after refactoring (no behavioral change)
2. ~3 new tests: YAML export, explicit 1% tolerance, Stroud import
3. Hand-calc cross-check: dual chute 250 MPH → 2 × ~26,600 lbs = ~53,200 lbs governing
4. Full regression: `PYTHONPATH=src uv run python -m pytest tests/structural/parachute/ -v`
