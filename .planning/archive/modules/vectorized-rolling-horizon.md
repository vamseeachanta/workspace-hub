# Regenerate Passing Ship Benchmark Report (WRK-131)

## Context

The benchmark report at `docs/modules/passing_ship/wang_benchmark/benchmark_report.html` is stale — generated before the formulation fix (commit `3f756872`). It shows 3 XFAIL, DEFECT badges, and a "Known Formulation Defects" section that no longer applies. Current test suite: **27 PASS, 5 SKIP, 0 FAIL**. The report generator also still uses raw conversion constants (`FT_TO_M=0.3048`) instead of the newly integrated `TrackedQuantity`.

## Scope

Single file modification: `src/digitalmodel/hydrodynamics/passing_ship/benchmark_report.py` (~336 → ~357 lines). Regenerate HTML output.

## Changes

### 1. Replace raw constants with TrackedQuantity

- Remove `FT_TO_M`, `LBF_TO_N`, `FT_LBF_TO_NM`, `SLUG_FT3_TO_KG_M3`
- Add `from assetutilities.units import TrackedQuantity` + `_tq()` helper
- Compute `REF_SWAY_KN` via `_tq(REF_SWAY_LBF, 'lbf').to('kN').magnitude`

### 2. Use `from_imperial()` factory in `_build_calculator()`

Replace manual `VesselConfig(length=950*FT_TO_M, ...)` with `PassingShipCalculator.from_imperial(moored_length_ft=950, ...)`. Pass `lateral_separation` and `passing_velocity` as TrackedQuantity-converted kwargs.

### 3. Add git SHA to report header

New `_get_git_sha()` helper (subprocess + try/except fallback). Display in header meta line.

### 4. Fix x-axis floating point noise

Round normalized stagger values to 6 decimal places in `_run_sweep()`.

### 5. Plot improvements

| Plot | Change |
|------|--------|
| Sweep plot (3-panel) | Add gridlines; add MathCAD ref markers for surge (~0) and yaw (~0) |
| Single DOF plots | Increase height 300px → 380px; add gridlines |
| All plots | Grid color `#ecf0f1` |
| Surge/yaw single | Pass `rv=0, rl="MathCAD ref (~0)"` |

### 6. Update `_TESTS` list — all PASS

Change 3 XFAIL entries to PASS:
- `("Magnitude", "Sway magnitude vs reference", "PASS", "0.04% error", "< 5%")`
- `("Symmetry", "Surge zero at abeam", "PASS", "~0 N", "~0")`
- `("Symmetry", "Surge antisymmetric in stagger", "PASS", "Antisymmetric", "Antisymmetric")`

### 7. Update DOF blocks — all PASS

| DOF | Badge | Key metric |
|-----|-------|------------|
| Surge | PASS (green) | Zero at abeam, antisymmetric |
| Sway | PASS (green) | Error vs MathCAD: ±0.04% |
| Yaw | PASS (green) | Zero at abeam (unchanged) |

Remove stale defect descriptions. Add correct formulation notes.

### 8. Update executive summary

- Badge: `PARTIAL` → `PASS`
- Counts: `27 PASS / 5 SKIP` (remove XFAIL row)
- Key finding: "All three DOFs match Wang (1975) / MathCAD reference"

### 9. Replace "Known Formulation Defects" → "Formulation Validation Summary"

New section documenting:
- Per-DOF accuracy table (sway error %, surge/yaw ~0)
- Fixes applied (kernel corrections, A₁×A₂ scaling)
- TOC link updated: `#defects` → `#validation`

### 10. Update unit conversion appendix

Replace raw constant values with `_tq(1, "ft").to("m").magnitude` etc.

### 11. Update vessel config rows

Replace `950*FT_TO_M` with `_tq(950, 'ft').to('m').magnitude` in table data.

## Files

| File | Action |
|------|--------|
| `src/digitalmodel/hydrodynamics/passing_ship/benchmark_report.py` | Modify (all changes) |
| `docs/modules/passing_ship/wang_benchmark/benchmark_report.html` | Regenerate |

## Verification

1. Run report generator: `uv run python -m digitalmodel.hydrodynamics.passing_ship.benchmark_report`
2. Open HTML and visually verify: all PASS badges, correct plots, no DEFECT/XFAIL
3. Run full test suite: `uv run python -m pytest tests/hydrodynamics/passing_ship/ -v` — expect 144 pass, 6 skip
4. Confirm sway at abeam ≈ 340 kN in report (vs 33,285 kN in old report)
