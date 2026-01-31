# V30 Financial Benchmark Tests — D&C, Leases, Economics

## Summary

Add granular benchmarking tests that verify drilling & completion days, lease data, and financial metrics against the V30 golden baseline. The V30 generator script (`generate_financial_summary_V30.py`) computed these from raw xlsx inputs — we now verify our Python pipeline reproduces them within tolerance.

## What We're Benchmarking

The golden baseline (`golden_baseline_v30.yml`) contains per-project:
- **D&C**: `dnc_total_usd`, `wellbores` (producers + injectors + exploration)
- **Financials**: `revenue_usd`, `royalty_usd`, `variable_opex_usd`, `fixed_opex_usd`, `net_cashflow_usd`, `npv_usd`, `mirr_monthly`, `mirr_annual`
- **CAPEX**: `facilities_cost_usd`
- **Wells**: `producers`, `injectors`, `wellbores`

Source data already loaded by existing functions:
- `load_v30_drilling()` → 219 wells × 12 columns (drilling days, completion days, depths, spud/TD dates)
- `load_v30_leases()` → 20 leases × 6 columns (lease-to-development mapping)
- `load_v30_assumptions()` → 39 assumptions × 7 columns (per dev-system cost rates)

## Plan — 3 Phases

### Phase 1: Create `test_v30_benchmarks.py` (TDD)

**File:** `tests/modules/lower_tertiary/test_v30_benchmarks.py`

#### A) Drilling & Completion Benchmarks

| Test | What it verifies |
|------|-----------------|
| `test_wellbore_counts_match_golden_baseline[{project}]` | Parametrized: wellbore count per development matches `wellbores` field in golden baseline |
| `test_all_developments_have_dnc_data` | All 10 golden baseline projects have D&C records |
| `test_drilling_days_positive_for_all_wells` | No negative or NaN drilling days |
| `test_spud_dates_precede_td_dates` | WELL_SPUD_DATE < TOTAL_DEPTH_DATE for all wells with both dates |
| `test_well_depths_reasonable` | MAX_BH_TOTAL_MD and MAX_WELL_BORE_TVD within 5,000–45,000 ft |
| `test_dnc_cost_reproduction[{project}]` | Parametrized: reproduce D&C total cost using V30 assumptions (day rates × days) within ±1% of golden baseline `dnc_total_usd` |

**D&C cost reproduction logic** (extracted from `generate_financial_summary_V30.py`):
- Drilling cost = drilling_days × MODU_LOADED_DAYRATE_MM × 1e6 (subsea15 rate for dry/pre-FO subsea20)
- Completion cost = completion_days × rate × 1e6 (DRY_TREE_RIG_RATE for dry, MODU rate for subsea)
- DnC_Total = sum of drilling + completion costs across all wells

#### B) Lease Data Benchmarks

| Test | What it verifies |
|------|-----------------|
| `test_lease_count_per_development` | Expected lease counts: JSM=6, CC=2, Anchor=2, etc. |
| `test_lease_to_development_mapping_complete` | All 20 V30 leases map to known developments |
| `test_dev_systems_match_golden_baseline[{project}]` | Parametrized: dev_system (subsea15/subsea20/dry/tieback15) matches golden baseline |
| `test_no_orphan_leases` | No leases without a DEV_NAME assignment |

#### C) Financial Benchmarks

| Test | What it verifies |
|------|-----------------|
| `test_revenue_matches_golden_baseline[{project}]` | Parametrized: revenue within ±0.1% of `revenue_usd` |
| `test_royalty_matches_golden_baseline[{project}]` | Parametrized: royalty within ±0.1% of `royalty_usd` |
| `test_variable_opex_matches_golden_baseline[{project}]` | Parametrized: variable opex within ±0.1% |
| `test_fixed_opex_matches_golden_baseline[{project}]` | Parametrized: fixed opex within ±0.1% |
| `test_facilities_cost_matches_golden_baseline[{project}]` | Parametrized: facilities CAPEX within ±1% |
| `test_net_cashflow_matches_golden_baseline[{project}]` | Parametrized: net cashflow within ±0.5% |
| `test_npv_matches_golden_baseline[{project}]` | Parametrized: NPV within ±1% |
| `test_mirr_matches_golden_baseline[{project}]` | Parametrized: MIRR within ±0.1% absolute |

### Phase 2: Create `v30_financial_reproducer.py`

**File:** `src/worldenergydata/analysis/lower_tertiary/v30_financial_reproducer.py`

Extracts the financial logic from `generate_financial_summary_V30.py` into a clean, testable module (~200 lines):

```python
def reproduce_v30_financials() -> dict[str, dict]:
    """Reproduce V30 financial summary from raw xlsx inputs.

    Loads leases, assumptions, OGOR production, D&C data, and WTI prices.
    Computes per-development: D&C costs, facilities CAPEX, revenue, royalty,
    opex, cashflow, NPV, MIRR — matching the V30 generator methodology.

    Returns dict keyed by development name with all financial metrics.
    """

def reproduce_dnc_costs(
    dnc_df: pd.DataFrame,
    assumptions: pd.DataFrame,
    dev_name: str,
    dev_system: str,
    first_oil: pd.Timestamp | None,
) -> dict[str, float]:
    """Reproduce D&C costs for a single development.

    Returns: drilling_cost_usd, completion_cost_usd, dnc_total_usd
    """
```

Key logic to port from `generate_financial_summary_V30.py`:
- **D&C day rates**: MODU_LOADED_DAYRATE for subsea, DRY_TREE_RIG_RATE for dry completions
- **Rate switching**: subsea20 pre-FO wells use subsea15 MODU rate
- **Facilities**: Host CAPEX spread over pre-FO months + SURF per well + booster/injection pumps + dry-tree well systems
- **Revenue/costs**: WTI × oil, royalty rate, variable opex/bbl, fixed opex/year
- **NPV/MIRR**: Monthly discount at 10% annual, trimmed cashflow window, Excel-like MIRR

### Phase 3: Run & verify

1. `uv run pytest tests/modules/lower_tertiary/test_v30_benchmarks.py -v` — All benchmark tests pass
2. `uv run pytest tests/modules/lower_tertiary/test_repeatability_v30.py -v` — V30 production regression: 12/12 (unchanged)
3. `uv run pytest tests/modules/lower_tertiary/ -v` — Full suite green

## Critical Files

| File | Action |
|------|--------|
| `tests/.../lower_tertiary/test_v30_benchmarks.py` | Create (~250 lines) |
| `src/.../lower_tertiary/v30_financial_reproducer.py` | Create (~200 lines) |
| `src/.../lower_tertiary/v30_reproducer.py` | No changes |
| `config/.../golden_baseline_v30.yml` | Read only (NEVER modified) |

## Tolerances (from golden baseline)

| Metric | Tolerance | Source |
|--------|-----------|--------|
| Production | ±0.1% | `production_relative: 0.001` |
| Revenue | ±0.1% | `revenue_relative: 0.001` |
| NPV | ±1% | `npv_relative: 0.01` |
| MIRR | ±0.001 | `mirr_absolute: 0.001` |
| Cashflow | ±0.5% | `cashflow_relative: 0.005` |

D&C, facilities, royalty, opex use ±0.1% (same as revenue).

## Key Invariant

`golden_baseline_v30.yml` is NEVER modified. The benchmark tests compare computed values against it.
