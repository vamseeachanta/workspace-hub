---
title: "WRK-115: Completion and Intervention Activity Analysis"
description: "Analyze completion and intervention activity trends in GOM using BSEE WAR data with rig fleet classification"
version: "1.0"
module: bsee/analysis
work_item: WRK-115
depends_on: [WRK-104]
session:
  id: ""
  agent: claude-opus-4-6
review:
  required_iterations: 3
  current_iteration: 0
  status: "planning"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 0
      feedback: ""
  ready_for_next_step: false
status: "draft"
progress: 0
created: "2026-02-08"
updated: "2026-02-08"
target_completion: ""
priority: "medium"
tags: [bsee, war, intervention, completion, rig-fleet, plotly]
links:
  spec: "specs/modules/completion-intervention-analysis.md"
  branch: ""
---

# WRK-115: Completion and Intervention Activity Analysis

> **Module**: bsee/analysis | **Status**: draft | **Created**: 2026-02-08

## Summary

Analyze completion and intervention activity trends in the Gulf of Mexico using BSEE WAR (Well Activity Report) data combined with the expanded rig fleet classification from WRK-104. The full WAR dataset (~2 million records) links each rig/unit to a well, lease, area, block, and date range. WRK-104 expanded the fleet from 16 sample rigs to 2,320 unique entities and revealed that 1,557 entities are NOT drilling rigs but rather intervention and completion equipment (wireline units, coil tubing units, lift boats, snubbing units, etc.). This module exploits that classification to produce time-series analysis of intervention vs. drilling activity across the GOM.

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini before implementation.

### Review Status

| Gate | Status |
|------|--------|
| Iterations (>= 3) | 0/3 |
| OpenAI Codex | pending |
| Google Gemini | pending |
| **Ready** | false |

### Review Log

| Iter | Date | Reviewer | Status | Feedback Summary |
|------|------|----------|--------|------------------|
| 1 | | Codex | Pending | |
| 1 | | Gemini | Pending | |
| 2 | | Codex | Pending | |
| 2 | | Gemini | Pending | |
| 3 | | Codex | Pending | |
| 3 | | Gemini | Pending | |

### Approval Checklist

- [ ] Iteration 1 complete (both reviewers)
- [ ] Iteration 2 complete (both reviewers)
- [ ] Iteration 3 complete (both reviewers)
- [ ] **APPROVED**: Ready for implementation

---

## Context

WRK-104 expanded the rig fleet dataset from 16 sample rigs to 2,320 unique entities extracted from the full BSEE WAR download (~2 million records). Classification revealed that 1,557 of these entities were initially "unknown" because they are NOT drilling rigs -- they are intervention and completion equipment:

| Category | Count | Examples |
|----------|-------|---------|
| Jack-up (reclassified) | 859 | ADRIATIC III, BLAKE 1006, CECIL PROVINE |
| Wireline Unit | 185 | BAKER ATLAS WIRELINE, * WIRELINE UNIT |
| Lift Boat | 176 | * LIFT BOAT, ARAPAHOE (LIFT BOAT) |
| Coil Tubing Unit | 68 | * COIL TUBING UNIT, * GENERIC COIL TUBING UNIT |
| Support Vessel | 56 | AMERICAN CONSTITUTION, * DIVE SUPPORT VESSEL |
| Snubbing Unit | 48 | * SNUBBING UNIT, APPLIED SNUBBING TECH #103 |
| Drillship (reclassified) | 19 | Various misclassified drillships |
| Platform Rig (reclassified) | 10 | AUGER TLP, various |
| Pumping Unit | 3 | Pumping units |
| Workover Rig | 1 | Workover rig |
| Remaining Unknown | 83 | Garbage entries, TBD placeholders, dates |

New `RigType` enum values added to support this classification: `WIRELINE_UNIT`, `COIL_TUBING_UNIT`, `LIFT_BOAT`, `SNUBBING_UNIT`, `WORKOVER_RIG`, `SUPPORT_VESSEL`, `PUMPING_UNIT`.

The existing rig fleet constants file (`src/worldenergydata/bsee/data/loaders/rig_fleet/constants.py`) already contains these enums along with the `classify_rig_type()` heuristic and `DataSource` enum.

## Objective

Build an analysis module that uses the expanded rig fleet classification to analyze completion and intervention activity trends in the Gulf of Mexico over time:

1. **Activity Volume by Equipment Type** -- Track WAR record counts per year for each intervention type (wireline, coil tubing, snubbing, lift boat, etc.)
2. **Drilling vs. Intervention Ratio** -- For each year/field/area, compute the fraction of WAR activity that is drilling vs. intervention/completion work
3. **Intervention Intensity by Field Maturity** -- Correlate intervention activity with field production decline; mature fields should show higher intervention-to-drilling ratios
4. **Equipment Fleet Composition Over Time** -- Track how the mix of active equipment has changed; identify whether wireline/coil tubing units are increasing relative to drilling rigs
5. **Seasonal and Cyclical Patterns** -- Identify seasonal patterns in intervention work (hurricane season effects, budget cycles)

## Data Sources

| Source | Description | Location |
|--------|-------------|----------|
| BSEE WAR data | Primary -- each record links a rig/unit name to a well, lease, area, block, and date range | `data/modules/bsee/.local/war/` |
| Rig fleet classification | Maps each WAR entity to a `RigType` (drilling rig vs. intervention equipment) | `data/modules/bsee/.local/rig_fleet/` or `data/modules/bsee/bin/rig_fleet/` |
| Rig type overrides CSV | Manual corrections for ambiguous names | `data/modules/bsee/bin/rig_fleet/rig_type_overrides.csv` |
| BSEE production data | For field maturity correlation (existing module) | Existing production loaders |

## Implementation Plan

### Phase 1: WAR Activity Aggregation Engine

**New file**: `src/worldenergydata/bsee/analysis/intervention/activity_aggregator.py` (~200 lines)

Core class: `WARActivityAggregator`

- Accept WAR DataFrame and classified rig fleet DataFrame as constructor inputs (dependency injection)
- Join WAR records to rig fleet on rig name to obtain `rig_type` for each record
- Group by `rig_type` and time period (year, quarter)
- Produce yearly activity counts by equipment category
- Output schema: DataFrame with columns `[year, rig_type, activity_count, unique_wells, unique_leases, unique_areas]`

Helper function: `classify_activity(rig_type: RigType) -> str`

- Returns `"drilling"` for drilling rig types: `DRILLSHIP`, `SEMI_SUBMERSIBLE`, `JACK_UP`, `PLATFORM_RIG`, `TENDER_ASSISTED`, `INLAND_BARGE`, `SUBMERSIBLE`
- Returns `"intervention"` for intervention types: `WIRELINE_UNIT`, `COIL_TUBING_UNIT`, `LIFT_BOAT`, `SNUBBING_UNIT`, `WORKOVER_RIG`, `SUPPORT_VESSEL`, `PUMPING_UNIT`
- Returns `"unknown"` for `UNKNOWN` and `LAND_RIG`

**Tests first** (`tests/modules/bsee/analysis/intervention/test_activity_aggregator.py`):

- [ ] Test `classify_activity()` for every `RigType` value
- [ ] Test aggregation with synthetic WAR DataFrame (10-20 rows)
- [ ] Test join logic when rig name not found in fleet (falls back to heuristic classifier)
- [ ] Test groupby produces correct counts per year/rig_type
- [ ] Test unique well/lease/area counting is distinct

### Phase 2: Drilling vs. Intervention Analysis

**New file**: `src/worldenergydata/bsee/analysis/intervention/drilling_vs_intervention.py` (~150 lines)

Core class: `DrillingInterventionAnalyzer`

- Accept aggregated activity DataFrame from Phase 1
- Compute drilling/intervention ratio by area, field, and year
- Produce summary DataFrame: `[year, area_code, drilling_count, intervention_count, ratio, pct_intervention]`
- Generate Plotly interactive charts:
  - Stacked bar chart: drilling vs. intervention activity per year
  - Line chart: intervention percentage over time by area
  - Heatmap: area vs. year with color = intervention ratio

**Tests first** (`tests/modules/bsee/analysis/intervention/test_drilling_vs_intervention.py`):

- [ ] Test ratio computation with known input values
- [ ] Test edge case: year with zero drilling activity (avoid division by zero)
- [ ] Test area-level grouping produces correct aggregates
- [ ] Test chart generation returns valid Plotly Figure objects

### Phase 3: Field Maturity Correlation

**New file**: `src/worldenergydata/bsee/analysis/intervention/field_maturity.py` (~200 lines)

Core class: `FieldMaturityCorrelator`

- Accept intervention activity data and production data as inputs
- Join on area/field identifiers
- Compute field maturity metrics: peak production year, production decline rate, cumulative production
- Correlate intervention frequency with production decline
- Identify case study fields: those where intervention activity rises as production declines
- Produce at least 3 concrete case studies with named fields

Output: DataFrame with columns `[field_name, area_code, peak_year, decline_rate_pct, intervention_count_post_peak, drilling_count_post_peak, intervention_ratio_post_peak]`

Plotly visualizations:

- Scatter plot: production rate vs. intervention frequency (one dot per field-year)
- Dual-axis line chart per case study field: production on left axis, intervention count on right axis

**Tests first** (`tests/modules/bsee/analysis/intervention/test_field_maturity.py`):

- [ ] Test maturity metric calculation with synthetic production data
- [ ] Test join between intervention and production datasets
- [ ] Test case study identification logic selects fields with declining production + rising intervention
- [ ] Test decline rate calculation correctness

### Phase 4: Fleet Composition Analysis

**New file**: `src/worldenergydata/bsee/analysis/intervention/fleet_composition.py` (~120 lines)

Core class: `FleetCompositionAnalyzer`

- Accept aggregated activity data from Phase 1
- Compute active equipment count per year by type
- Compute percentage share of each equipment type per year
- Identify trends: which types are growing/shrinking relative to others

Plotly visualizations:

- 100% stacked area chart: equipment type share over time
- Line chart: absolute count of active units per type per year

**Tests first** (`tests/modules/bsee/analysis/intervention/test_fleet_composition.py`):

- [ ] Test percentage share calculation sums to 100% per year
- [ ] Test trend detection identifies increasing/decreasing types
- [ ] Test with synthetic data spanning multiple years

### Phase 5: Seasonal Pattern Detection

**New file**: `src/worldenergydata/bsee/analysis/intervention/seasonal_patterns.py` (~120 lines)

Core class: `SeasonalPatternDetector`

- Accept WAR data with date columns
- Aggregate activity by month across all years
- Compute seasonal index: monthly activity / annual average
- Identify hurricane season effects (June-November) vs. other months
- Detect budget cycle patterns (Q4 surge, Q1 slowdown)

Plotly visualizations:

- Polar/radar chart: monthly intervention activity index
- Box plot: monthly activity distributions across years

**Tests first** (`tests/modules/bsee/analysis/intervention/test_seasonal_patterns.py`):

- [ ] Test seasonal index calculation with uniform data (all indices = 1.0)
- [ ] Test hurricane season months are correctly identified
- [ ] Test aggregation by month produces 12 data points

### Phase 6: Interactive Dashboard

**New file**: `src/worldenergydata/bsee/analysis/intervention/dashboard.py` (~200 lines)

Core class: `InterventionDashboard`

- Orchestrate all analysis components (Phases 1-5)
- Produce a combined Plotly HTML dashboard using `plotly.subplots.make_subplots`
- Include filter controls for area, time range, and equipment type
- Export to `reports/bsee/intervention/`

Dashboard sections:

1. Activity volume by equipment type (stacked bar)
2. Drilling vs. intervention ratio trend (dual-axis line)
3. Fleet composition over time (stacked area)
4. Field maturity scatter (scatter with trendline)
5. Seasonal patterns (radar chart)

**Tests first** (`tests/modules/bsee/analysis/intervention/test_dashboard.py`):

- [ ] Test dashboard generation produces valid HTML string
- [ ] Test dashboard includes expected number of subplots
- [ ] Test file export writes to correct path

## Critical Files

| File | Action |
|------|--------|
| `src/worldenergydata/bsee/analysis/intervention/__init__.py` | **New** |
| `src/worldenergydata/bsee/analysis/intervention/activity_aggregator.py` | **New** |
| `src/worldenergydata/bsee/analysis/intervention/drilling_vs_intervention.py` | **New** |
| `src/worldenergydata/bsee/analysis/intervention/field_maturity.py` | **New** |
| `src/worldenergydata/bsee/analysis/intervention/fleet_composition.py` | **New** |
| `src/worldenergydata/bsee/analysis/intervention/seasonal_patterns.py` | **New** |
| `src/worldenergydata/bsee/analysis/intervention/dashboard.py` | **New** |
| `tests/modules/bsee/analysis/intervention/__init__.py` | **New** |
| `tests/modules/bsee/analysis/intervention/test_activity_aggregator.py` | **New** |
| `tests/modules/bsee/analysis/intervention/test_drilling_vs_intervention.py` | **New** |
| `tests/modules/bsee/analysis/intervention/test_field_maturity.py` | **New** |
| `tests/modules/bsee/analysis/intervention/test_fleet_composition.py` | **New** |
| `tests/modules/bsee/analysis/intervention/test_seasonal_patterns.py` | **New** |
| `tests/modules/bsee/analysis/intervention/test_dashboard.py` | **New** |

## Reuse Existing Code

- `RigType` enum and `classify_rig_type()` from `src/worldenergydata/bsee/data/loaders/rig_fleet/constants.py`
- `RigFleetLoader` from `src/worldenergydata/bsee/data/loaders/rig_fleet/rig_fleet_loader.py` for loading classified fleet
- `WARDataAcquirer` from `src/worldenergydata/bsee/data/loaders/rig_fleet/war_acquirer.py` for loading WAR data
- Rig type overrides CSV at `data/modules/bsee/bin/rig_fleet/rig_type_overrides.csv`
- Existing BSEE production data loaders for Phase 3 field maturity correlation

## Dependency Order

```
Phase 1 (activity aggregator) ── foundation for all subsequent phases
         |
         +── Phase 2 (drilling vs. intervention) ── depends on Phase 1
         |
         +── Phase 4 (fleet composition) ── depends on Phase 1
         |
         +── Phase 5 (seasonal patterns) ── uses raw WAR data, minimal Phase 1 dependency
         |
Phase 3 (field maturity) ── depends on Phase 2 + production data
         |
Phase 6 (dashboard) ── depends on all previous phases
```

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| WRK-104 (Rig Fleet Expansion) | COMPLETED | Provides classified fleet with intervention types |
| BSEE production data loader | Existing | For field maturity correlation in Phase 3 |
| WAR data acquirer | Existing | From WRK-104, provides raw WAR DataFrame |
| Plotly | Existing | Already in project dependencies |
| pandas | Existing | Already in project dependencies |

## Success Criteria

1. Activity trend charts show at least 20 years of WAR data by equipment type
2. Drilling vs. intervention ratio visible at area level
3. At least 3 field maturity correlation case studies with named GOM fields
4. All outputs as interactive HTML (Plotly)
5. Full test coverage on the aggregation engine (Phase 1)
6. All tests pass: `uv run pytest tests/modules/bsee/analysis/intervention/ -v`
7. Dashboard exports to `reports/bsee/intervention/` as self-contained HTML

## Verification

1. `uv run pytest tests/modules/bsee/analysis/intervention/ -v` -- all tests pass
2. Run full analysis with WAR data: `uv run python -m src.worldenergydata.bsee.analysis.intervention.dashboard`
3. Verify HTML reports generated in `reports/bsee/intervention/`
4. Confirm charts show data spanning at least 20 years
5. Confirm at least 3 field maturity case studies are identified
6. `uv run pytest` -- full test suite passes without regressions

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Review Iteration 1 | Pending | |
| Review Iteration 2 | Pending | |
| Review Iteration 3 | Pending | |
| Plan Approved | Pending | |
| Phase 1: WAR Activity Aggregation Engine | Pending | |
| Phase 2: Drilling vs. Intervention Analysis | Pending | |
| Phase 3: Field Maturity Correlation | Pending | |
| Phase 4: Fleet Composition Analysis | Pending | |
| Phase 5: Seasonal Pattern Detection | Pending | |
| Phase 6: Interactive Dashboard | Pending | |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-08 | | claude-opus-4-6 | Plan created |
