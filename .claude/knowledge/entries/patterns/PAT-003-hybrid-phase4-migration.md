---
id: PAT-003
type: pattern
title: "Hybrid Phase 4 migration for multi-case scripts"
category: orcaflex
tags: [orcaflex, phase4, migration, reporting, sensitivity-analysis]
repos: [digitalmodel]
confidence: 0.9
created: "2026-02-24"
last_validated: "2026-02-24"
source_type: session
related: [ADR-001]
status: active
access_count: 0
---

# Hybrid Phase 4 Migration for Multi-Case Scripts

## Problem

Phase 4 is a single-case, single-structure report framework. Legacy OrcFxAPI
post-processing scripts often run sensitivity analyses (tension × environment ×
heading sweeps) across many `.sim` files — a many-to-one relationship that cannot
be directly replaced by a Phase 4 wrapper.

## Solution

Use a **hybrid migration** approach:

- **Phase 4 extractors** handle data extraction and CSV side-effects
  (`build_report_from_model()`, `export_rangegraph_csvs()`)
- **Domain script** retains sensitivity rendering logic (Plotly charts, HTML
  page generation, summary tables)
- **Phase 4 summary** is generated once from the base case sim, with all
  worst-case UCs mapped to `DesignCheckData`

```python
# Per-sim: use Phase 4 extractor for CSV export
if PHASE4_AVAILABLE:
    export_rangegraph_csvs(lines=[pipeline], variables=VARS,
                           period=period_rg, output_dir=sim_rg_dir)

# Post-loop: build one Phase 4 summary from base case
if PHASE4_AVAILABLE and _phase4_report is not None:
    _phase4_report.design_checks = DesignCheckData(
        code="DNV-OS-F101",
        checks=[UtilizationData(...) for case, util, arc in _worst_utils],
    )
    generate_orcaflex_report(_phase4_report, output_path)
```

## When to Use

- Any legacy script that loops over multiple `.sim` files
- Scripts that perform sensitivity / parametric sweeps
- Cases where full Phase 4 migration would require rewriting multi-case chart logic

## Guard Pattern

Always wrap Phase 4 imports in a `try/except` with a `PHASE4_AVAILABLE` flag so
the script remains runnable in environments without the `digitalmodel` package:

```python
try:
    from digitalmodel.solvers.orcaflex.reporting... import ...
    PHASE4_AVAILABLE = True
except ImportError:
    PHASE4_AVAILABLE = False
```

## Validated In

WRK-315 — 24in pipeline installation postproc scripts (2026-02-24)
