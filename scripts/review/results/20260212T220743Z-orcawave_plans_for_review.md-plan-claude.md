# Review by Claude
# Source: orcawave_plans_for_review.md
# Type: plan
# Date: 20260212T220743Z

[Claude review requires interactive session or API call]
## Content to Review
```
---
id: WRK-130
title: "Standardize analysis reporting for each OrcaWave structure type"
status: pending
priority: high
complexity: complex
compound: false
created_at: 2026-02-11T19:00:00Z
target_repos:
  - digitalmodel
commit:
spec_ref:
related: [WRK-125, WRK-129, WRK-031, WRK-115]
blocked_by: []
synced_to: []
plan: inline
plan_reviewed: false
plan_approved: false
percent_complete: 0
brochure_status:
tags: [reporting, orcawave, diffraction, html-reports, standardization, analysis-outputs, plotly]
---

# Standardize Analysis Reporting for Each OrcaWave Structure Type

## What
Create a standardized reporting framework for OrcaWave (diffraction) analysis outputs, with per-hull-type report templates. Each hull category (barge, ship, spar, semi-sub, FPSO, LNGC) gets a dedicated HTML report with consistent format: RAO plots per DOF, added mass/damping matrices, wave excitation forces, mesh quality summary, and solver comparison tables.

## Why
- Diffraction benchmark reports (barge r4, ship r1, spar r1) were built ad-hoc with custom scripts
- The r4 barge report format is the canonical template but not yet abstracted into reusable code
- Standard reports enable automated post-processing after every OrcaWave/AQWA run
- Consistent format across hull types makes cross-comparison straightforward
- Links to hull library (WRK-115) — reports should auto-reference cataloged hull metadata

## Scope
1. **Define standard diffraction output schema** — RAOs (6 DOF × N headings × N frequencies), added mass (6×6), radiation damping (6×6), wave excitation forces, mesh metadata
2. **Report template** — single-page HTML following r4 barge report convention (per-DOF 2-col grid, significance filter, vertical legends)
3. **Standard plots** — RAO amplitude/phase per DOF, added mass/damping vs frequency, wave force per heading
4. **Solver comparison** — side-by-side OrcaWave vs AQWA (vs BEMRosetta) when multiple solver results available
5. **Mesh quality section** — panel count, aspect ratio, watertight check, symmetry
6. **Report generator API** — `generate_diffraction_report(hull_id, solver_results) → HTML`
7. **Integration with hull catalog** — auto-populate hull metadata from `hull_panel_catalog.yaml`

## Acceptance Criteria
- [ ] Standard diffraction output schema defined (RAOs, matrices, forces, mesh)
- [ ] HTML report template following r4 barge canonical format
- [ ] Plotly interactive plots: RAO amplitude/phase, added mass/damping matrices, wave forces
- [ ] Solver comparison layout when multiple results available
- [ ] Mesh quality summary section with panel statistics
- [ ] Report generator callable from benchmark scripts
- [ ] At least 2 example reports generated from existing benchmark data (barge, ship or spar)
- [ ] Reports self-contained (single HTML file with embedded Plotly CDN)

## Plan

**Target**: `src/digitalmodel/hydrodynamics/diffraction/report_generator.py` (new) + extend `benchmark_plotter.py`

### Existing Assets (reuse)

| Component | Path | Purpose |
|-----------|------|---------|
| BenchmarkPlotter | `hydrodynamics/diffraction/benchmark_plotter.py` | r4 barge report rendering (HTML + Plotly) |
| BenchmarkRunner | `hydrodynamics/diffraction/benchmark_runner.py` | `_generate_html_report()` + `_generate_json_report()` |
| BenchmarkReport | `hydrodynamics/diffraction/multi_solver_comparator.py` | Report dataclass (consensus, per-DOF results) |
| GeometryQualityReport | `hydrodynamics/diffraction/geometry_quality.py` | Mesh quality metrics + recommendations |
| ComparisonReport | `hydrodynamics/diffraction/comparison_framework.py` | Solver-vs-solver comparison |
| RAO Plotter | `hydrodynamics/diffraction/rao_plotter.py` | Per-DOF RAO plots (amplitude + phase) |
| r4 barge report | `benchmark_output/barge_benchmark/r4_per_dof_report/` | Canonical HTML template |
| Hull catalog | `data/hull_library/catalog/hull_panel_catalog.yaml` | Hull metadata (23 entries) |
| PanelCatalogEntry | `hydrodynamics/hull_library/panel_catalog.py` | Pydantic model for hull metadata |
| Benchmark scripts | `scripts/benchmark/regenerate_barge_benchmark.py`, `regenerate_ship_benchmark.py`, `run_spar_benchmark.py` | Per-hull benchmark orchestration |

### Phase 1 — Define Standard Diffraction Output Schema

- Create `DiffractionReportData` Pydantic model in `report_generator.py`:
  - `hull_metadata`: from `PanelCatalogEntry` (name, dimensions, panel count, symmetry)
  - `solver_results`: Dict[solver_name, SolverOutput] — RAOs (6 DOF × N headings × N freqs), added mass (6×6 × N freqs), radiation damping (6×6 × N freqs), wave excitation forces
  - `mesh_quality`: from `GeometryQualityReport` (panel count, aspect ratio, watertight, symmetry)
  - `comparison`: from `BenchmarkReport` (consensus level, per-DOF agreement)
  - `metadata`: solver versions, run dates, frequency/heading grids, unit systems
- Ensure schema can be serialized to JSON for archival

### Phase 2 — Extract & Refactor r4 Report Template

- Extract the inline HTML/CSS from `benchmark_plotter._render_html_with_table()` into a Jinja2-style template or string template
- Canonical layout (from r4 barge):
  - Header: hull name, dimensions, draft, displacement, solver names
  - Per-DOF sections: 2-col grid (45% text + table left, 55% Plotly plot right)
  - Significance filter: auto-omit headings < 1% of peak response
  - Vertical legends: right side, grouped by heading
  - Solver-column tables: headings as rows, solver names as columns
  - CSS: alternating rows, hover highlight, monospace numerics (Cascadia Code)
- Plotly conventions: `include_plotlyjs=False` + CDN, right margin 140+px, `tracegroupgap=2`

### Phase 3 — Report Generator API

- `generate_diffraction_report(report_data: DiffractionReportData, output_path: Path) -> Path`
- Sections generated:
  1. **Hull Summary** — auto-populated from `hull_panel_catalog.yaml` via hull_id lookup
  2. **Mesh Quality** — panel stats, aspect ratio histogram, watertight check
  3. **RAO Plots** — amplitude + phase per DOF, all headings overlaid
  4. **Added Mass & Damping** — diagonal elements vs frequency, off-diagonal matrix heatmap
  5. **Wave Excitation** — force/moment per DOF per heading
  6. **Solver Comparison** — side-by-side tables + overlay plots (when 2+ solvers)
  7. **Summary Table** — peak values per DOF, natural periods, consensus level
- Single self-contained HTML file with embedded Plotly CDN script tag

### Phase 4 — Per-Hull-Type Customization

Define hull-type-specific report tweaks (all share the base template):

| Hull Type | Customization |
|-----------|--------------|
| Barge | All 6 DOFs relevant, rectangular symmetry note |
| Ship | Note on roll damping (viscous), forward speed effects |
| Spar | Heave/pitch dominant, surge coupling note, deep draft context |
| Semi-sub | Column/pontoon interference, low-frequency resonance highlight |
| FPSO | Weathervaning note, turret position, spread mooring comparison |
| LNGC | Membrane tank sloshing note, side-by-side operation context |

- Implement as `HullTypeConfig` dict mapping hull category to display hints
- Auto-detect category from `hull_panel_catalog.yaml` entry

### Phase 5 — Integration & Validation

- Wire `generate_diffraction_report()` into existing benchmark scripts:
  - `regenerate_barge_benchmark.py` → call after benchmark completes
  - `regenerate_ship_benchmark.py` → same
  - `run_spar_benchmark.py` → same
- Generate 2 example reports from existing benchmark data (barge r4, ship r1)
- Verify: reports load in browser, Plotly interactive, all sections populated
- Unit tests: report generation with mock data (no solver dependency)

---
*Source: reporting for each structure in the orcawave module. standardize analysis outputs*
---
id: WRK-131
title: "Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response"
status: pending
priority: high
complexity: complex
compound: false
created_at: 2026-02-11T21:00:00Z
target_repos:
  - digitalmodel
commit:
spec_ref:
related: [WRK-039, WRK-125, WRK-129, WRK-130]
blocked_by: []
synced_to: []
plan: inline
plan_reviewed: false
plan_approved: false
percent_complete: 0
brochure_status:
tags: [passing-ship, mooring, aqwa, hydrodynamics, port-engineering, force-calculation]
---

# Passing Ship Analysis for Moored Vessels

## What
Build a passing ship analysis capability for moored vessels. Calculate hydrodynamic forces on a moored vessel due to a passing ship (surge, sway, yaw), evaluate mooring line tensions under passing ship events, and generate standardized reports. Covers perpendicular and parallel passing cases, with/without wind, at varying speeds and distances.

## Why
- Passing ship effects are a critical design case for port/terminal mooring systems
- ~15+ historical projects demonstrate recurring demand for this analysis type
- Currently relies on standalone Excel tool (`PassingShipForceCalculator.xlsm`) and manual AQWA runs
- Standardizing into the digitalmodel framework enables parametric studies, consistent reporting, and reuse

## Resources (local, not in repo)
- **Tool**: `G:\ACMA Tool\Passing Ships\` — existing passing ship force calculator (Excel-based)
- **Archive**: `R:\Archive - Drive J\` — ~15+ past project folders with AQWA models, reports, and results
- **Key tool files**: `PassingShipForceCalculator.xlsm` (force calculation), `PassingShipForceCalculator 3.7 knot.xlsm` (speed variant)
- **Output examples**: Line tension plots at various passing speeds (3.0 knot, 3.7 knot), mooring line groups (1-6, 7-12)

## Technical Scope
1. **Passing ship force model** — hydrodynamic interaction forces (surge, sway, yaw) as function of:
   - Passing ship speed, size (displacement, length, beam, draft)
   - Moored vessel dimensions
   - Separation distance (lateral)
   - Water depth / depth-to-draft ratio
   - Passing angle (parallel, perpendicular, oblique)
2. **Mooring response** — time-domain mooring analysis with passing ship force time history:
   - Line tensions per mooring line
   - Vessel motions (surge, sway, yaw excursions)
   - Fender loads
   - Combined with wind, current, wave (with/without passing vessel scenarios)
3. **Analysis cases** — parametric matrix:
   - Wind with passing vessel / wind without passing vessel
   - Perpendicular passing / parallel passing
   - Multiple passing speeds
   - Short ship / long ship variants
4. **PassingShipForceCalculator extraction** — reverse-engineer the Excel tool logic into Python
5. **AQWA integration** — passing ship force application in AQWA mooring analysis (or OrcaFlex equivalent)
6. **Reporting** — standardized HTML report per WRK-129 convention

## PassingShipSpec — Analysis Specification
Create a `PassingShipSpec` (similar to `DiffractionSpec` pattern) that fully defines a passing ship analysis:
- **Moored vessel**: hull geometry, mooring arrangement, loading condition, RAOs
```
## Review Prompt
# Plan Review Prompt

You are reviewing a technical plan/specification for a software engineering project. Evaluate the following aspects:

## Review Criteria

1. **Completeness**: Are all requirements addressed? Are there missing acceptance criteria?
2. **Feasibility**: Is the proposed approach technically sound? Are there hidden complexities?
3. **Dependencies**: Are all dependencies identified? Are there circular or missing dependencies?
4. **Risk**: What are the top 3 risks? Are mitigation strategies adequate?
5. **Scope**: Is the scope well-defined? Is there scope creep risk?
6. **Testing**: Is the test strategy adequate? Are edge cases considered?

## Output Format

Provide your review as:

### Verdict: APPROVE | REQUEST_CHANGES | REJECT

### Summary
[1-3 sentence overall assessment]

### Issues Found
- [P1] Critical: [issue description]
- [P2] Important: [issue description]
- [P3] Minor: [issue description]

### Suggestions
- [suggestion 1]
- [suggestion 2]

### Questions for Author
- [question 1]
- [question 2]
