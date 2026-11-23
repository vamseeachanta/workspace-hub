---
name: openfoam-analysis
description: "End-to-end CFD analysis workflow using OpenFOAM \u2014 from problem\
  \ definition through meshing, solving, and post-processing to calculation report\
  \ generation. Integrates with calculation-methodology (6-phase structure) and calculation-report\
  \ (YAML \u2192 HTML rendering). Use when performing CFD analyses, not just setting\
  \ up cases.\n"
type: reference
version: 1.0.0
updated: 2026-03-16
category: engineering/cfd
triggers:
- cfd analysis
- openfoam analysis
- run cfd
- cfd calculation
- flow simulation
- drag calculation
- wave loading cfd
- openfoam run
tags:
- openfoam
- cfd
- analysis
- workflow
- calculation
- marine
- drag
- vof
- convergence
platforms:
- linux
depends_on:
- openfoam
- gmsh-meshing
- calculation-methodology
- calculation-report
capabilities:
- analysis_execution
- convergence_monitoring
- post_processing
- calculation_report_generation
requires:
- OpenFOAM v2312
see_also:
- openfoam
- gmsh-meshing
- freecad-automation
- calculation-report
---

# OpenFOAM Analysis Workflow

> Run CFD analyses end-to-end: define → mesh → solve → validate → report.
> Reference skill (`openfoam`) has dict syntax; this skill has the workflow.

## Quick Start

```bash
# 1. Define analysis in YAML
cp references/analysis-templates/current-drag.yaml my-analysis.yaml
# Edit: geometry, flow conditions, mesh parameters

# 2. Run analysis
bash scripts/openfoam-analysis/run-analysis.sh my-analysis.yaml

# 3. Generate calculation report
uv run --no-project python scripts/openfoam-analysis/generate-calc-yaml.py my-analysis.yaml
uv run --no-project python scripts/reporting/generate-calc-report.py my-analysis-calc.yaml
```

## Workflow Stages

This skill maps to the calculation-methodology 6-phase structure:

| Stage | Calc-Methodology Phase | Micro-skill | Key Output |
|-------|----------------------|-------------|------------|
| 1 | Phase 1: Problem Definition | `stage-01-problem-definition.md` | Analysis YAML with scope, objective, acceptance criteria |
| 2 | Phase 2-3: Inputs + Method | `stage-02-case-setup.md` | OpenFOAM case directory with all dicts |
| 3 | — (CFD-specific) | `stage-03-meshing.md` | Validated mesh (checkMesh PASS) |
| 4 | Phase 4: Computation | `stage-04-execution.md` | Converged solution + logs |
| 5 | Phase 5: Validation | `stage-05-post-processing.md` | Extracted results + validation checks |
| 6 | Phase 6: Reporting | `stage-06-reporting.md` | calculation-report YAML → HTML |

## Analysis Templates

Pre-configured templates in `references/analysis-templates/`:

| Template | Solver | Physics | Marine Use Case |
|----------|--------|---------|-----------------|
| `current-drag.yaml` | simpleFoam | Steady RANS k-omega SST | Drag on subsea structures |
| `wave-loading.yaml` | interFoam | VOF + waves2Foam | Wave forces on fixed platforms |
| `cavity-benchmark.yaml` | icoFoam | Laminar transient | Validation benchmark |
| `dambreak-benchmark.yaml` | interFoam | VOF laminar | Validation benchmark |

## Environment

```bash
# Source before any OpenFOAM operation (script handles this automatically)
source /usr/lib/openfoam/openfoam2312/etc/bashrc 2>/dev/null || true
```

**Key learning:** OpenFOAM bashrc has unbound variables — never use `set -u` in scripts.
Tutorials with `0.orig/` require `cp -r 0.orig 0` before running.

## Script Reference

| Script | Purpose |
|--------|---------|
| `run-analysis.sh` | Orchestrate full analysis from YAML config |
| `check-convergence.py` | Parse solver log, detect divergence, plot residuals |
| `extract-results.py` | Extract forces, pressures, free surface from results |
| `generate-calc-yaml.py` | Convert analysis results to calculation-report YAML |
| `run-openfoam-tutorials.sh` | Run benchmark tutorials for validation |

## Convergence Criteria

| Field | Target (steady) | Target (transient) | Divergence threshold |
|-------|-----------------|-------------------|---------------------|
| p | initial < 1e-4 | final < tolerance | initial > 1e+6 |
| U | initial < 1e-4 | final < tolerance | initial > 1e+6 |
| k, omega | initial < 1e-4 | final < tolerance | initial > 1e+6 |
| Continuity (local) | < 1e-4 | < 1e-4 | > 1e-1 |

## Integration with Calculation Methodology

Every CFD analysis produces a calculation YAML with these sections:

```yaml
metadata:
  title: "Current Drag on Subsea Manifold"
  standard: "DNV-RP-C205 Environmental Conditions and Environmental Loads"

inputs:
  - {name: "Current velocity", symbol: "U_c", value: 1.2, unit: "m/s", source: "Metocean report"}
  - {name: "Water depth", symbol: "d", value: 85, unit: "m"}
  - {name: "Structure diameter", symbol: "D", value: 2.5, unit: "m"}

methodology:
  description: "CFD analysis using OpenFOAM simpleFoam with k-omega SST turbulence model"
  standard: "DNV-RP-C205 §6 Current Loads"
  equations:
    - {id: "eq1", name: "Drag force", latex: "F_D = \\frac{1}{2} \\rho C_D A U^2"}
    - {id: "eq2", name: "Reynolds number", latex: "Re = \\frac{U D}{\\nu}"}

outputs:
  - {name: "Drag coefficient", symbol: "C_D", value: null, unit: "-", pass_fail: true, limit: "<2.0"}
  - {name: "Drag force", symbol: "F_D", value: null, unit: "kN"}

assumptions:
  - "Steady-state flow (no wave-current interaction)"
  - "Smooth surface (no marine growth)"

references:
  - "DNV-RP-C205:2021 Environmental Conditions and Environmental Loads"
  - "OpenFOAM v2312 ESI Group"
```

The `generate-calc-yaml.py` script populates `value: null` fields from OpenFOAM results.

## Mesh Quality Gates

Analysis will not proceed to solver execution if mesh fails these checks:

| Metric | Pass | Fail |
|--------|------|------|
| Non-orthogonality max | < 70 | ≥ 70 |
| Skewness | < 4 | ≥ 4 |
| Aspect ratio | < 100 | ≥ 100 |
| Negative volumes | 0 | > 0 |

## Error Handling

Each stage validates before passing to the next. On failure:
1. Diagnostic YAML written to `<case>/diagnostics.yaml`
2. Exit code propagated (non-zero = failure)
3. Partial results preserved for debugging

Refer to `openfoam` skill §4 (Failure Diagnosis) for root cause analysis.
