# worldenergydata Calculation Audit

Generated: 2026-03-13 | WRK-1179 Stream B Task 4

## Summary Statistics

| Metric | Count |
|--------|-------|
| Calculation modules (files with calc logic) | 42 |
| Data loader modules (files, approximate) | 548 |
| Identified calculation gaps | 7 |
| Tests passed (with available deps) | 230 |
| Tests failed (infra/fixture issues) | 3 |
| Tests errored (missing deps: sklearn, metocean_stats, schedule) | 18+ |
| Tests skipped | 14 |

## Data Loader Modules (summary only)

| Directory | Module count | Description |
|-----------|-------------|-------------|
| bsee/ | 208 | Bureau of Safety and Environmental Enforcement |
| sodir/ | 27 | Norwegian Petroleum Directorate (Sodir) |
| eia/ + eia_us/ | 11 | Energy Information Administration |
| canada/ | 14 | Canada energy regulator |
| mexico_cnh/ | 8 | Mexico CNH hydrocarbon data |
| texas_rrc/ | 13 | Texas Railroad Commission |
| brazil_anp/ | 5 | Brazil ANP oil and gas |
| ukcs/ | 6 | UK Continental Shelf |
| lng_terminals/ | 27 | LNG terminal data |
| vessel_fleet/ + vessel_hull_models/ | 68 | Marine vessel data |
| marine_safety/ | 71 | Marine safety incident data |
| metocean/ | 50 | Metocean statistics (EVA, contours) |
| hse/ | 17 | Health, safety, environment data |
| lower_tertiary/ + west_africa/ + landman/ | 22 | Regional/specialized loaders |
| marine/ | 1 | Marine general |

**Total data-loader modules: ~548**

## Calculation Modules (detailed breakdown)

### 1. Production Forecast / Decline Curves

**Directory:** `production/forecast/`

| File | Key functions | Description |
|------|--------------|-------------|
| `decline.py` | `ArpsDeclineCurve.fit`, `forecast`, `plot` | Full Arps decline curve analysis: exponential (b=0), hyperbolic (0<b<2), harmonic (b=1). scipy curve_fit. EUR computation. Plotly visualization. |
| `cli.py` | `run` | CLI entry point for decline analysis |

**Status:** Fully implemented. All three Arps models (exponential, hyperbolic, harmonic) with R-squared goodness-of-fit, EUR at economic limit, and confidence intervals dataclass (not yet populated). WRK-318 may be closeable.

### 2. Production Unified / Cross-Basin Analysis

**Directory:** `production/unified/`

| File | Key functions | Description |
|------|--------------|-------------|
| `cross_basin.py` | `compare_peak_rates`, `compare_cumulative_eur`, `fiscal_sensitivity` | Cross-basin production comparison and fiscal sensitivity |
| `normalizer.py` | `validate`, `normalize`, `build_summary`, `find_coverage_gaps` | Production data normalization |
| `router.py` | `list_regions`, `get_adapter`, `resolve_regions` | Multi-region adapter routing |
| `adapters/` (8 files) | `fetch`, `available_fields`, `date_range` | Per-region data adapters (BSEE, EIA, Sodir, UKCS, Brazil ANP, Canada, Mexico CNH, Texas RRC) |

**Status:** Data access layer complete. Cross-basin comparison is analytical but not a calculation engine.

### 3. Economics / DCF

**Directory:** `economics/`

| File | Key functions | Description |
|------|--------------|-------------|
| `dcf.py` | `calculate_npv`, `calculate_mirr`, `build_cash_flow_schedule` | Full NPV and MIRR implementation. CashFlowSchedule integrates capex, opex, revenue, carbon cost, emission volumes. |
| `carbon.py` | `carbon_npv_curve`, `breakeven_carbon_price`, `tornado_sensitivity` | Carbon cost sensitivity: NPV sweep over carbon prices, Brent root-finding for breakeven, tornado chart data generation. |

**Status:** Fully implemented. NPV/MIRR with carbon cost sensitivity is complete (addresses WRK-321). Tornado sensitivity covers oil price, opex, carbon price, and discount rate.

### 4. Cost Calibration

**Directory:** `cost/calibration/`

| File | Key functions | Description |
|------|--------------|-------------|
| `cost_predictor.py` | `fit`, `predict`, `predict_batch`, `cross_validate`, `training_r2_score` | ML-based cost prediction with linear regression. Cross-validation support. |

**Status:** Implemented but requires `sklearn` (not in current deps). Tests error on import.

### 5. Well Bore Design

**Directory:** `well_bore_design/`

| File | Key functions | Description |
|------|--------------|-------------|
| `hydraulics.py` | `annular_velocity_fps`, `pressure_loss_psi_per_100ft`, `ecd_ppg`, `hole_cleaning_index`, `compare_bore_types` | Drilling hydraulics calculations |
| `decision_framework.py` | `recommend`, `pressure_window_check` | Bore type recommendation based on pressure windows |
| `schemas.py` | `bore_type_from_bit_size`, `pressure_window_ppg`, `is_safe_at_all_depths`, `safe_depth_fraction` | Well bore classification and safety checks |

**Status:** Implemented. Hydraulics calculations (ECD, pressure loss, annular velocity) and bore type decision framework.

### 6. Drilling Batch Economics

**Directory:** `drilling/batch_economics/`

| File | Key functions | Description |
|------|--------------|-------------|
| `bsee_batch_detector.py` | `detect_batches`, `fit_learning_curve` | Batch drilling detection from BSEE data, learning curve fitting |
| `economics.py` | `learning_curve_time`, `mobilization_savings`, `break_even_n_wells`, `batch_vs_standalone_npv`, `campaign_total_cost` | Batch vs standalone economics, learning curve time estimation, NPV comparison |

**Status:** Implemented. Learning curve economics and batch drilling cost analysis.

### 7. Drilling Pressure Management / MPD

**Directory:** `drilling_pressure_management/`

| File | Key functions | Description |
|------|--------------|-------------|
| `fleet_mpd.py` | `get_mpd_capable_rigs`, `fleet_mpd_summary` | MPD-capable rig fleet analysis |
| `mpd_configurations.py` | `analyze`, `ecd_pressure`, `mpd_required` | MPD system configuration analysis and ECD pressure calculation |
| `mpd_systems.py` | `get_system`, `systems_summary` | MPD system catalog |

**Status:** Partially calculation, partially data catalog. ECD pressure and MPD-required determination are calculations; fleet/system lookups are data.

### 8. Decommissioning

**Directory:** `decommissioning/`

| File | Key functions | Description |
|------|--------------|-------------|
| `cost_model.py` | `estimate`, `estimate_campaign`, `total_cost_musd`, `cost_by_region`, `from_calibration` | Decommissioning cost estimation |
| `cost_calibration.py` | `fit`, `calibration_result`, `fitted_factors`, `synthetic_removal_dataframe` | Cost model calibration against actuals |
| `late_life.py` | `assess_field`, `screen_portfolio`, `late_life_fields` | Late-life field screening |
| `data_completeness.py` | `score`, `portfolio_scores` | Data quality scoring |
| `regulations.py` | `get_regulations`, `get_lead_time`, `regulatory_summary` | Regulatory lookup (data, not calc) |

**Status:** Cost estimation and calibration are genuine calculations. Late-life screening is analytical.

### 9. Pipeline Safety / Fitness-for-Service

**Directory:** `pipeline_safety/`

| File | Key functions | Description |
|------|--------------|-------------|
| `workflow.py` | `characterize`, `assess_ffs`, `assess`, `generate_report`, `verdict_summary` | Pipeline fitness-for-service assessment workflow |

**Status:** FFS assessment workflow implemented. PHMSA data importer provides source data.

### 10. Safety Analysis

**Directory:** `safety_analysis/`

| File | Key functions | Description |
|------|--------------|-------------|
| `calibrator.py` | `fit`, `risk_score`, `assess`, `calibrated_matrix_df` | Risk model calibration |
| `analysis/correlation.py` | `crosscorr`, `compute`, `compute_rolling` | Cross-correlation analysis |
| `analysis/decomposition.py` | `decompose_signal`, `remove_trend_and_seasonality` | Time series decomposition |
| `analysis/feature_engineering.py` | `compute_statistical_features`, `compute_fft_features` | Feature engineering for ML |
| `analysis/statistical_tests.py` | `ttest_two_groups`, `anova_test`, `chi_square_test`, `pearson_correlation`, `linear_regression_summary` | Statistical hypothesis tests |
| `analysis/time_series.py` | `calculate_gradient`, `calculate_moving_average`, `normalize_by_active_assets` | Time series analysis |
| `analysis/incident_aggregation.py` | `compute_hurt_index`, `compute_time_series_hurt_index` | Incident severity aggregation |
| `nlp/` (5 files) | `train`, `predict`, `embed_texts`, `fit_transform` | NLP classification (TF-IDF, BERT) |
| `risk_index/scorer.py` | `score` | Composite risk index scoring |
| `risk_index/normalizer.py` | `percentile_rank`, `normalize_to_scale` | Score normalization |
| `taxonomy/incident_classifier.py` | `classify`, `classify_batch` | Incident classification |

**Status:** Substantial calculation module. Statistical analysis, time series decomposition, NLP classification, and risk scoring.

### 11. FDAS (Field Development Analysis System)

**Directory:** `fdas/`

| File | Key functions | Description |
|------|--------------|-------------|
| `core/financial.py` | `excel_like_mirr`, `calculate_npv`, `calculate_irr`, `calculate_payback_period`, `calculate_all_metrics` | Full financial metrics suite |
| `analysis/cashflow.py` | `generate_monthly_cashflow`, `calculate_net_cashflow`, `calculate_host_capex_timing` | Monthly cashflow generation |
| `data/drilling.py` | `calculate_drilling_days`, `classify_activity`, `extract_mud_weight` | Drilling activity analysis |
| `data/production.py` | `aggregate_monthly_production`, `exponential_decline` | Production aggregation with decline |

**Status:** Complete field development economics system. Parallel to `economics/` module but BSEE-specific with Excel-compatible MIRR.

### 12. Well Planning

**Directory:** `well_planning/`

| File | Key functions | Description |
|------|--------------|-------------|
| `risk_analyzer.py` | `risk_matrix`, `escalation_report`, `high_priority_risks` | Drilling risk analysis |
| `risk_calibrator.py` | `calibrate`, `risk_probability`, `calibration_report` | Risk model calibration against HSE data |

**Status:** Risk analysis and calibration calculations implemented.

### 13. Well Production Dashboard (embedded calcs)

**Directory:** `well_production_dashboard/`

| File | Key functions | Description |
|------|--------------|-------------|
| `views_decline.py` | `fit_exponential_decline`, `fit_hyperbolic_decline`, `forecast_production`, `calculate_eur` | Decline curve fitting (duplicate of `production/forecast/decline.py`) |
| `views_financial.py` | `calculate_revenue`, `calculate_npv`, `calculate_irr`, `calculate_payback_period` | Financial calculations (duplicate of `economics/dcf.py` and `fdas/core/financial.py`) |
| `well_production.py` | `calculate_npv`, `calculate_decline_rate`, `forecast_production` | More duplicated calc functions |

**Status:** Contains duplicated calculation logic from other modules. Refactoring opportunity.

## Identified Calculation Gaps

| # | Gap | Priority | Notes |
|---|-----|----------|-------|
| 1 | Type curve matching / normalization | HIGH | Cross-basin has `compare_peak_rates` but no type curve fitting (Blasingame, Fetkovich) |
| 2 | Resource estimation (probabilistic P10/P50/P90) | HIGH | No Monte Carlo or probabilistic resource estimation module exists |
| 3 | Drilling cost per foot benchmarking | MEDIUM | `drilling/batch_economics/` has learning curves but no cost/ft normalization or benchmarking across formations |
| 4 | Production forecasting beyond Arps | MEDIUM | No DCA alternatives: stretched exponential (SEPD), power-law exponential, Duong method for unconventionals |
| 5 | Pore pressure prediction | MEDIUM | `drilling_pressure_management/` has ECD/MPD but no pore pressure from logs (Eaton, Bowers methods) |
| 6 | Confidence intervals on decline curves | LOW | `ForecastResult` has `lower_ci`/`upper_ci` fields but they are never populated |
| 7 | Duplicate calculation consolidation | LOW | Decline curve and NPV/IRR logic duplicated across `production/forecast/`, `economics/`, `fdas/`, and `well_production_dashboard/` |

### Gap relationship to existing WRKs

- **WRK-318** (Arps decline curves): Largely addressed -- exponential, hyperbolic, harmonic all implemented in `production/forecast/decline.py`
- **WRK-321** (NPV/MIRR with carbon cost sensitivity): Fully addressed in `economics/dcf.py` + `economics/carbon.py`

## Test Results

```
Tests passed: 230
Tests failed: 3 (infrastructure/fixture issues)
Tests skipped: 14
Tests errored: 18+ (missing optional deps: sklearn, metocean_stats, schedule)
```

Missing dependencies causing test errors:
- `sklearn` -- needed by `cost/calibration/`, `sodir/forecasting.py`, `ukcs/production/decline_curves.py`, `bsee/analysis/forecasting/`
- `metocean_stats` -- needed by `metocean/statistics/`
- `schedule` -- needed by `scheduler/`

## Observations

1. **Strong economics stack**: NPV, MIRR, carbon sensitivity, tornado charts, and FDAS financial metrics are all well-implemented with proper dataclass outputs.
2. **Arps decline curves complete**: All three classical models with scipy curve_fit, R-squared, and EUR computation.
3. **Significant duplication**: Decline curve and financial calculations exist in at least 3-4 locations. A consolidation pass would reduce maintenance burden.
4. **Dependency gaps**: `sklearn` is used in several modules but not reliably in the dependency group, causing test failures.
5. **Data-heavy codebase**: ~548 data-loader modules vs ~42 calculation modules. The repo is primarily a data aggregation platform with calculation capabilities layered on top.
