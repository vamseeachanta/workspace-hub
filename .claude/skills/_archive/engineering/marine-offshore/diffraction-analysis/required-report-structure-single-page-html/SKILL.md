---
name: diffraction-analysis-required-report-structure-single-page-html
description: 'Sub-skill of diffraction-analysis: Required Report Structure (Single-Page
  HTML) (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Required Report Structure (Single-Page HTML) (+3)

## Required Report Structure (Single-Page HTML)


1. **Header** — Vessel name, date, overall consensus badge
2. **Input Comparison** — Solver-column table (geometry, mass, environment, damping)
3. **Consensus Summary** — Per-DOF badges (FULL/SPLIT/NO_CONSENSUS)
4. **Per-DOF Analysis** — 2-column grid: text/conclusions left (45%), Plotly plot right (55%)
5. **Full Overlay Plots** — Combined amplitude/phase across all DOFs
6. **Notes** — Auto-generated observations

## Required Plot Conventions


- **Vertical legends** on right side (`x=1.02, y=1.0, orientation="v"`)
- **Heading-first trace ordering** (group solvers under each heading in legend)
- **Significance filtering** — auto-omit headings where response < 1% of DOF peak
- **Monospace fonts** for all numeric values (Cascadia Code / Consolas)

## Required Table Conventions


- Solver names as column headers, headings as rows
- Alternating row colors, hover highlight, dark header theme
- Section separator rows for grouping

## Reference Implementation


- Plotter: `src/digitalmodel/hydrodynamics/diffraction/benchmark_plotter.py`
- Runner: `src/digitalmodel/hydrodynamics/diffraction/benchmark_runner.py`
- Example output: `benchmark_output/barge_benchmark/r4_per_dof_report/`
