---
name: clean-code-top-p1-candidates-2026-02-25-audit
description: 'Sub-skill of clean-code: Top P1 Candidates (2026-02-25 audit).'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Top P1 Candidates (2026-02-25 audit)

## Top P1 Candidates (2026-02-25 audit)


**digitalmodel** (active development + oversized):

| File | Lines | Domain | Status | Split Strategy |
|------|-------|--------|--------|----------------|
| `hydrodynamics/diffraction/benchmark_plotter.py` | 2700 | Hydro | ✅ DONE (WRK-592/593) | Horizontal split: helpers, rao_plots, correlation, input_reports + shims |
| `hydrodynamics/diffraction/report_generator.py` | 2034 | Hydro | ✅ DONE (WRK-591/593) | data_models, computations, extractors, builders_header/hydrostatics/responses |
| `solvers/orcaflex/orcaflex_model_components.py` | 1905 | Solvers | Open | Extract: line-types, vessel, environment, post-process |
| `marine_ops/marine_analysis/visualization/integration_charts.py` | 1439 | Marine | Open | Extract by chart type |

**worldenergydata** (active development + oversized):

| File | Lines | Domain | Status | Split Strategy |
|------|-------|--------|--------|----------------|
| `cost/data_collection/public_dataset.py` | 1643 | Cost | Open | Extract: fetcher, parser, normalizer, schema |
| `safety_analysis/taxonomy/activity_taxonomy.py` | 1550 | Safety | ✅ DONE (WRK-590) | activity_definitions (data, exempt) + activity_registry (logic) |
| `well_production_dashboard/field_aggregation.py` | 1131 | Dashboard | Open | Extract: query, aggregate, format |
| `well_production_dashboard/well_production.py` | 1090 | Dashboard | Open | Extract: models, fetcher, renderer |

---
