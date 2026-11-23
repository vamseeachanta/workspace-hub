---
name: orcawave-aqwa-benchmark-html-report-structure
description: 'Sub-skill of orcawave-aqwa-benchmark: HTML Report Structure (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# HTML Report Structure (+1)

## HTML Report Structure


```python
from digitalmodel.diffraction.comparison_framework import BenchmarkReporter

# Initialize reporter
reporter = BenchmarkReporter()

# Generate comprehensive report
reporter.generate_html_report(
    comparison_results=results,
    output_file="reports/benchmark_report.html",

*See sub-skills for full details.*

## Report Sections (r4 Canonical Format)


The r4 benchmark report format is the **standard template for all diffraction analysis**. All new benchmark and diffraction reports must follow this structure:

1. **Header** — Vessel name, date, overall consensus badge
2. **Input Comparison** — Solver-column table (geometry, mass, environment, damping)
3. **Consensus Summary** — Per-DOF badges (FULL/SPLIT/NO_CONSENSUS)
4. **Per-DOF Analysis** — 2-col grid: text/conclusions left (45%), Plotly plot right (55%)
5. **Full Overlay Plots** — Combined amplitude/phase across all DOFs
6. **Notes** — Auto-generated observations

Reference implementation: `benchmark_plotter.py` + `benchmark_runner.py`
