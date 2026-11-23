# Terminal 2 — Field Development Economics Facade Review

## Issue: #1858 — Integrate worldenergydata FDAS + economics into field development workflow

## What was found at session start

The economics facade (`economics.py`, 474 lines) was **substantially complete**:
- `EconomicsInput` dataclass with validation (all 5 fiscal regimes)
- `CostEstimates`, `EvaluationMetrics`, `EconomicsResult` output types
- CAPEX adapter → `digitalmodel.field_development.capex_estimator` (GoM benchmark)
- ABEX adapter → `worldenergydata.decommissioning.DecommissioningCostEstimator`
- Financial adapter → `worldenergydata.fdas.calculate_all_metrics` (with numpy fallback)
- OPEX estimation → `digitalmodel.field_development.opex_estimator`
- Cashflow construction with CAPEX spread, plateau/decline, carbon cost
- `evaluate_economics()` entry point
- `__init__.py` exports all public names
- 35 passing tests

## Missing delta identified from issue checklist

| Issue checkbox | Status before | After |
|---|---|---|
| Create economics.py as facade | Done | — |
| Import worldenergydata.fdas for NPV/IRR/MIRR | Done | — |
| **Import worldenergydata.cost for CAPEX estimation** | **Missing** | **Wired** |
| Import worldenergydata.economics for DCF + carbon sensitivity | Partial | **Wired** |
| Import worldenergydata.decommissioning for ABEX | Done | — |
| Wire fiscal regime selection | Done | — |
| Create unified input schema | Done | — |
| Wire into field_development/workflow.py (#1848) | Not started | Deferred (separate issue scope) |

## Changes made

### 1. `economics.py` — CostPredictor CAPEX adapter (primary path)
- `_resolve_capex_adapter()` now tries `worldenergydata.cost.CostPredictor` first
- Constructs a valid `CostDataPoint` probe from `EconomicsInput` fields
- Maps water_depth_m → WaterDepthBand, host_type → SubseaType/RigType
- Falls back to GoM benchmark on ImportError or any CostPredictor failure

### 2. `economics.py` — `build_economics_schedule()` CashFlowSchedule bridge
- Builds a `worldenergydata.economics.dcf.CashFlowSchedule` from `EconomicsInput`
- Populates `emission_tco2_per_period` for carbon sensitivity recomputation
- Accepts optional pre-computed cost overrides
- Schedule is directly consumable by `calculate_npv`, `calculate_mirr`, `carbon_npv_curve`

### 3. `economics.py` — `carbon_sensitivity()` pass-through
- Wraps `worldenergydata.economics.carbon.carbon_npv_curve`
- Default sweep: [0, 25, 50, 75, 100, 150, 200] USD/tCO2
- Returns `CarbonSensitivityResult` with NPV array + base NPV

### 4. `__init__.py` — exports updated
- Added `build_economics_schedule` and `carbon_sensitivity` to imports and `__all__`

### 5. `test_economics.py` — 15 new tests (50 total)
- 3 CostPredictor wiring tests (fallback, mocked primary, override bypass)
- 7 CashFlowSchedule bridge tests (type, length, emissions, CAPEX/revenue, overrides, NPV integration)
- 5 carbon sensitivity tests (type, default prices, custom prices, monotonicity, base NPV)

## Test results

```
50 passed in 34.81s
```

No regressions. All 35 original tests pass. All 15 new tests pass.

## Remaining work for #1858

- `workflow.py` integration (#1848 scope) — not created, deferred to its own issue
- CostPredictor live integration test — requires sklearn + dataset in digitalmodel test env
