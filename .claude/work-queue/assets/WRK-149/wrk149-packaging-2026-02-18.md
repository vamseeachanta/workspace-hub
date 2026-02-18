# WRK-149 Packaging Snapshot (2026-02-18)

## Scope Completed in This Batch
- Stabilized legacy `asset_integrity` tests to avoid import-time execution and to skip gracefully when external library files are unavailable.
- Added focused new test modules for priority coverage work:
  - `src/digitalmodel/asset_integrity/tests/test_update_deep_additional.py`
  - `src/digitalmodel/asset_integrity/tests/test_yml_utilities_additional.py`
  - `tests/hydrodynamics/diffraction/test_polars_exporter_additional.py`
  - `tests/hydrodynamics/hull_library/test_catalog_additional.py`

## High-Value Module Coverage (Focused)
- `digitalmodel.asset_integrity.common.update_deep`: **100.00%**
- `digitalmodel.hydrodynamics.diffraction.polars_exporter`: **99.14%**
- `digitalmodel.hydrodynamics.hull_library.catalog`: **94.70%**
- `digitalmodel.hydrodynamics.hull_library.rao_registry`: **99.04%**
- `digitalmodel.asset_integrity.common.yml_utilities`: **84.76%**

## Broad Priority Baseline Trend
- Earlier broad run total: **6.05%**
- Latest broad run total: **7.85%**
- Delta: **+1.80 percentage points**

Note: Broad baseline still has pre-existing failures in large scope suites (seed-data and environment dependent). Changed-file regression suite for WRK-149 edits is green.

## Changed-File Regression Result
- Result: **53 passed, 17 skipped, 0 failed**
- Command style: `uv run python -m pytest ...`

## Files Added
- `src/digitalmodel/asset_integrity/tests/test_update_deep_additional.py`
- `src/digitalmodel/asset_integrity/tests/test_yml_utilities_additional.py`
- `tests/hydrodynamics/diffraction/test_polars_exporter_additional.py`
- `tests/hydrodynamics/hull_library/test_catalog_additional.py`

## Files Updated
- `src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_ecs_2500ft_buoy_jt.py`
- `src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_multi_process.py`
- `src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_parallel_process.py`
- `src/digitalmodel/asset_integrity/tests/test_pyintegrity_bs7910_single_process.py`
- `src/digitalmodel/asset_integrity/tests/test_pyintegrity_gml_lml_api579.py`

## Suggested Commit Split (if desired)
1. `test(asset_integrity): WRK-149 stabilize legacy pyintegrity tests for collection`
2. `test(hydrodynamics): WRK-149 add coverage for polars exporter and hull catalog`
3. `test(asset_integrity): WRK-149 extend unit coverage for update_deep and yml_utilities`

## Cross-Review Record
- Claude review file: `scripts/review/results/20260218T040220Z-wrk149-packaging-2026-02-18.md-implementation-claude.md`
  - Normalized verdict: `APPROVE`
- Gemini review file: `scripts/review/results/20260218T040220Z-wrk149-packaging-2026-02-18.md-implementation-gemini.md`
  - Normalized verdict: `ERROR` (output did not contain a parseable review verdict)
