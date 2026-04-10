## Context
Follow-up to #1861 (scaffold commit `aaf90c8e`). The benchmark bridge provides equipment count statistics (trees, manifolds, tieback distances). This issue correlates those with cost data to build unit cost curves.

## Scope
- [ ] Correlate SubseaIQ equipment counts with `worldenergydata` cost public dataset
- [ ] Build unit cost curves: cost/tree, cost/km-flowline, cost/manifold
- [ ] Cross-validate against 71 sanctioned project costs (from existing capex_estimator data)
- [ ] Output cost benchmark bands by water depth and concept type

## Target Files
- `digitalmodel/src/digitalmodel/field_development/benchmarks.py` (extend with cost functions)
- `worldenergydata/subseaiq/analytics/` (cost correlation helpers)
- `digitalmodel/tests/field_development/test_benchmarks.py` (extend)

## Depends On
- #1861 (scaffold — done)
- SubseaIQ scraping with equipment count fields
- worldenergydata cost.public_dataset availability