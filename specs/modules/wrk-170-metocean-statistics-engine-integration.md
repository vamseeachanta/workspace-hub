---
title: "WRK-170: Metocean Statistics Engine — metocean-stats Integration"
description: "Statistical analysis subpackage for worldenergydata metocean module"
version: "1.0"
module: metocean/statistics
session:
  id: wrk-170-plan
  agent: claude-opus-4-6
review: pending
---

# WRK-170: Metocean Statistics Engine

## Context

The worldenergydata metocean module has **12K+ lines, 5 data clients, full CLI, DB, caching** — but **zero production statistical analysis code**. A GEV block-maxima EVA prototype exists in `tests/modules/metocean/test_skill_statistics.py` (546 lines) but was never promoted to production. Scatter diagrams, joint probability, environmental contours, and weather windows are all described in skill docs but not implemented.

[MET-OM/metocean-stats](https://github.com/MET-OM/metocean-stats) (MIT, 98 stars) provides production-grade implementations of all these methods. This plan creates a thin wrapper layer that:
- Makes core methods (EVA, scatter, weather windows) work with **scipy only** (zero new deps)
- Optionally delegates to metocean-stats for advanced methods (CMA joint probability, IDM)
- Optionally uses virocon for environmental contours (IFORM/ISORM)

## Dependency Strategy: 3-Tier

| Tier | Requirement | Capabilities |
|------|-------------|-------------|
| **0 (always)** | scipy + numpy (already installed) | Block maxima GEV, POT GPD, scatter diagrams, weather windows |
| **1 (optional)** | `pip install worldenergydata[metocean-stats]` | IDM, directional extremes, CMA joint models |
| **2 (optional)** | `pip install worldenergydata[metocean-contours]` | IFORM, ISORM, highest-density contours via virocon |

Backend detection at import time; `StatisticsBackendError` with install hint if user calls unavailable function.

## New Files

```
src/worldenergydata/metocean/statistics/
├── __init__.py                  (~60L)   Public API re-exports
├── _backends.py                 (~80L)   Backend detection + lazy imports
├── _converters.py               (~120L)  HarmonizedObservation ↔ DataFrame bridge
├── results.py                   (~200L)  Frozen result dataclasses
├── eva.py                       (~350L)  Block maxima GEV + POT GPD + optional IDM
├── joint_probability.py         (~300L)  Scatter diagrams + optional CMA
├── environmental_contours.py    (~250L)  Optional IFORM/ISORM via virocon
├── weather_windows.py           (~250L)  Threshold operability + persistence
└── report.py                    (~350L)  Plotly HTML report assembly

tests/modules/metocean/
├── test_statistics_eva.py       (~300L)
├── test_statistics_joint.py     (~200L)
├── test_statistics_contours.py  (~150L)  Skip if virocon not installed
├── test_statistics_weather.py   (~200L)
└── test_statistics_report.py    (~200L)
```

**Total**: ~10 new source files, ~5 test files, ~3,500 LOC

## Modified Files

- `worldenergydata/pyproject.toml` — add optional dependency groups
- `src/worldenergydata/metocean/__init__.py` — add statistics re-exports

## Key Design Decisions

1. **Optional dependency with fallback** — metocean-stats is NOT a hard requirement; core EVA + scatter + weather windows work with scipy only
2. **Data bridge via `_converters.py`** — single conversion point from `HarmonizedObservation` → DataFrame; all stats functions accept DataFrames directly
3. **Frozen result dataclasses** — `EVAResult`, `ScatterDiagramResult`, `ContourResult`, `WeatherWindowResult` with `.to_dataframe()` methods
4. **Plotly-only visualization** — never call metocean-stats matplotlib plots; extract numerical data, build Plotly traces from scratch (SN comparison report pattern)
5. **No CLI in this WRK** — API-first; CLI deferred
6. **Synthetic test data** — embedded generators (like existing EVA test), no network calls

## Implementation Phases

### Phase 1: Foundation (~460 LOC)
- `_backends.py` — detect metocean-stats/virocon availability
- `_converters.py` — HarmonizedObservation list → time-indexed DataFrame, validate record length
- `results.py` — all result dataclasses (EVAResult, ScatterDiagramResult, ContourResult, WeatherWindowResult, JointProbabilityResult)
- `__init__.py` (stub)

### Phase 2: EVA Engine (~650 LOC)
Promote existing prototype from `test_skill_statistics.py` into production `eva.py`:
- `return_levels_block_maxima()` — GEV/Gumbel via scipy MLE, annual maxima extraction, bootstrap CIs, KS + QQ diagnostics
- `return_levels_pot()` — GPD fitting, automatic threshold (percentile), 48h declustering, bootstrap CIs
- `return_levels_idm()` — optional, requires metocean-stats
- Tests: monotonic return levels, CI bracketing, reproducibility, minimum record validation

### Phase 3: Joint Probability + Contours (~850 LOC)
- `scatter_diagram()` — 2D binning (numpy only), occurrence counts + probabilities
- `fit_joint_model()` — CMA via metocean-stats (optional), Hs-Tp model
- `compute_contour()` / `compute_multi_contours()` — IFORM/ISORM via virocon (optional)
- `contour_data_coverage()` — validation: T-year contour should enclose ~(1-1/T) of data
- Tests: scatter bin counts, contour enclosure percentage (skip if virocon absent)

### Phase 4: Weather Windows (~550 LOC)
- `analyze_operability()` — multi-threshold, AND/OR combine, monthly + overall %
- `weather_window_statistics()` — individual window start/end/duration
- `monthly_operability_table()` — months × thresholds matrix
- Tests: manual threshold verification, window identification, edge cases (no windows, all operable)

### Phase 5: Reports (~500 LOC)
- `plot_return_levels()` — return period curve + CIs + empirical points
- `plot_scatter_diagram()` — Plotly heatmap
- `plot_contours()` — contour overlay on scatter data
- `plot_operability_heatmap()` — monthly × threshold heatmap
- `generate_statistics_report()` — combined HTML report (Plotly CDN, JSON traces, summary tables)
- Tests: HTML content assertions, figure trace counts

### Phase 6: Wiring (~100 LOC)
- Final `__init__.py` with conditional exports
- `pyproject.toml` optional dependency groups
- `metocean/__init__.py` update

### Phase 7: Worked Examples (~400 LOC)
- **Gulf of Mexico EVA**: synthetic NDBC-42035-style data → block maxima + POT → scatter diagram → HTML
- **North Sea Operability**: synthetic hindcast → weather windows at Hs=1.5/2.0/2.5/3.0m → monthly heatmap → HTML

## Key Reference Files

| File | Purpose |
|------|---------|
| `worldenergydata/src/worldenergydata/metocean/processors/data_harmonizer.py` | `HarmonizedObservation` dataclass — bridge source |
| `worldenergydata/tests/modules/metocean/test_skill_statistics.py` | EVA prototype (546L) — promote to production |
| `digitalmodel/src/digitalmodel/structural/fatigue/sn_comparison_report.py` | Plotly HTML report pattern |
| `worldenergydata/src/worldenergydata/metocean/clients/base_client.py` | `FetchResult[T]` pattern |
| `worldenergydata/pyproject.toml` | Dependency management |

## Verification

```bash
# Run all statistics tests (Tier 0 — scipy only)
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/modules/metocean/test_statistics_*.py -v --tb=short --noconftest

# Verify existing metocean tests still pass
PYTHONPATH="src:../assetutilities/src" python3 -m pytest tests/modules/metocean/ -v --tb=short --noconftest

# Verify HTML report output (spot check)
PYTHONPATH="src:../assetutilities/src" python3 -c "
from worldenergydata.metocean.statistics import return_levels_block_maxima, plot_return_levels
# ... quick smoke test
"
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| metocean-stats incompatible with Python 3.12 | Tier 0 works without it |
| virocon C dependency compilation | Contours are Tier 2 optional |
| File size > 400 lines | One file per analysis type; largest is ~350L |
| Existing test EVA code breaks on promotion | Keep test file, refactor to import from `eva.py` |
