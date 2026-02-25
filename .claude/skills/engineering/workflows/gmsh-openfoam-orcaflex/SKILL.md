---
name: gmsh-openfoam-orcaflex
description: >
  Multi-physics simulation pipeline — Gmsh mesh generation → OpenFOAM CFD →
  OrcaFlex structural/mooring analysis.  Agent-callable end-to-end workflow
  that passes geometry, fluid loads, and structural response through three
  solvers in sequence with validated handoffs at each step.  Stub/mock
  fallbacks for environments without solver licenses.
version: 1.0.0
updated: 2026-02-24
category: workflow
triggers:
  - multi-physics pipeline
  - Gmsh OpenFOAM OrcaFlex
  - CFD to structural pipeline
  - fluid loads to OrcaFlex
  - hydrodynamic structural chain
  - H1 multi-physics workflow
  - cylinder in flow pipeline
  - gmsh openfoam orcaflex
capabilities:
  - input_generation
  - execution
  - output_parsing
  - failure_diagnosis
  - validation
  - stub_mode
requires:
  - gmsh-meshing
  - openfoam
  - orcaflex-modeling
  - cfd-pipeline
see_also:
  - hydrodynamic-pipeline
  - cfd-pipeline
  - orcawave-to-orcaflex
wrk_ref: WRK-380
spec_ref: specs/modules/wrk-380-gmsh-openfoam-orcaflex-pipeline.md
---

# Gmsh → OpenFOAM → OrcaFlex Multi-Physics Pipeline Skill

Agent-callable end-to-end workflow for hydrodynamic-to-structural analysis.
Runs Gmsh mesh generation, OpenFOAM CFD, and OrcaFlex structural analysis
in sequence with validated handoffs.  All three solvers have stub fallbacks.

## Quick Invocation

```bash
# Real mode (all three solvers installed)
python3 scripts/pipelines/gmsh_openfoam_orcaflex.py \
    --diameter 1.0 --length 5.0 --velocity 1.5 \
    --work-dir /tmp/pipeline_run

# Stub mode (no solver licenses required — CI / ace-linux-1)
python3 scripts/pipelines/gmsh_openfoam_orcaflex.py \
    --diameter 1.0 --length 5.0 --velocity 1.5 \
    --work-dir /tmp/pipeline_run --stub-mode

# Shell wrapper
bash scripts/pipelines/gmsh_openfoam_orcaflex.sh \
    --diameter 1.0 --length 5.0 --velocity 1.5 --stub-mode

# Run full test suite (no solvers required)
cd scripts/pipelines && python3 -m pytest test_cylinder_in_flow.py -v
```

## Pipeline Architecture

```
Parameters (D, L, U)
       │
┌──────▼──────────────────────────────────────────────────────┐
│ Stage 1: Gmsh mesh generation                                │
│   stub_gmsh.py  OR  gmsh Python API                         │
│   Output: work_dir/mesh.msh                                  │
└──────┬───────────────────────────────────────────────────────┘
       │ mesh.msh
┌──────▼──────────────────────────────────────────────────────┐
│ Gate 1: Mesh quality check                                   │
│   validate_mesh_quality.py                                   │
│   Checks: max_skewness < 4.0, non-orthog < 70°, cells > 100 │
│   FAIL → abort with structured report                        │
└──────┬───────────────────────────────────────────────────────┘
       │ pass
┌──────▼──────────────────────────────────────────────────────┐
│ Converter 1: Gmsh .msh → OpenFOAM polyMesh                  │
│   convert_gmsh_to_openfoam.py                                │
│   Uses: gmshToFoam CLI (preferred) or meshio (fallback)     │
│   Stub mode: skipped (stub solver writes its own output)     │
└──────┬───────────────────────────────────────────────────────┘
       │ constant/polyMesh/
┌──────▼──────────────────────────────────────────────────────┐
│ Stage 3: OpenFOAM CFD simulation                             │
│   stub_openfoam.py  OR  simpleFoam                          │
│   Output: log.simpleFoam + postProcessing/forces/0/force.dat │
└──────┬───────────────────────────────────────────────────────┘
       │ force.dat
┌──────▼──────────────────────────────────────────────────────┐
│ Gate 2: CFD convergence + force balance                      │
│   validate_cfd_convergence.py                                │
│   Checks: all residuals < 1e-4, force balance error < 5%    │
│   FAIL → abort with residual log                             │
└──────┬───────────────────────────────────────────────────────┘
       │ pass
┌──────▼──────────────────────────────────────────────────────┐
│ Converter 2: OpenFOAM forces → OrcaFlex load CSV            │
│   convert_openfoam_to_orcaflex.py                            │
│   Output: loads.csv (Time, Fx, Fy, Fz, Mx, My, Mz)         │
└──────┬───────────────────────────────────────────────────────┘
       │ loads.csv
┌──────▼──────────────────────────────────────────────────────┐
│ Stage 5: OrcaFlex structural/mooring analysis                │
│   stub_orcaflex.py  OR  OrcFxAPI                            │
│   Output: max_deflection_m, max_tension_N                    │
└──────┬───────────────────────────────────────────────────────┘
       │
   pipeline_results.json  (PASS / FAIL per gate + final metrics)
```

## File Map

```
scripts/pipelines/
├── gmsh_openfoam_orcaflex.py      # Pipeline orchestrator (main entry point)
├── gmsh_openfoam_orcaflex.sh      # Shell wrapper
├── validate_mesh_quality.py       # Gate 1: mesh quality checker
├── validate_cfd_convergence.py    # Gate 2: CFD convergence + force balance
├── convert_gmsh_to_openfoam.py    # Converter 1: .msh → polyMesh
├── convert_openfoam_to_orcaflex.py # Converter 2: force.dat → loads.csv
├── test_cylinder_in_flow.py       # End-to-end test (stub mode, 40 tests)
└── stubs/
    ├── stub_gmsh.py               # Gmsh stub: writes synthetic .msh
    ├── stub_openfoam.py           # OpenFOAM stub: writes log + force.dat
    └── stub_orcaflex.py           # OrcaFlex stub: beam theory deflection
```

## Output Format: pipeline_results.json

```json
{
  "version": "1.0.0",
  "parameters": {"diameter_m": 1.0, "length_m": 5.0, "velocity_m_s": 1.5},
  "passed": true,
  "stages": {
    "gmsh":                {"passed": true, "cell_count": 980, ...},
    "gate1_mesh_quality":  {"passed": true, "max_skewness": 0.4, ...},
    "convert_gmsh_to_foam":{"passed": true, "method": "gmshToFoam", ...},
    "openfoam":            {"passed": true, "drag_force_N": 5765.6, ...},
    "gate2_cfd_convergence":{"passed": true, "converged": true, ...},
    "convert_foam_to_orcaflex":{"passed": true, "row_count": 50, ...},
    "orcaflex":            {"passed": true, "max_deflection_m": 0.002, ...}
  },
  "summary": {
    "drag_force_N": 5765.62,
    "max_deflection_m": 0.002,
    "max_tension_N": 6210.5,
    "mesh_cells": 980,
    "stub_mode": true
  }
}
```

## Validation Gates

### Gate 1 — Mesh Quality

| Metric | Limit | Source |
|--------|-------|--------|
| Max skewness | < 4.0 | OpenFOAM checkMesh default |
| Max non-orthogonality | < 70 deg | OpenFOAM checkMesh default |
| Cell count | >= 100 | Pipeline minimum |

Gate uses `checkMesh` when OpenFOAM is sourced; falls back to gmsh Python API
quality metric; falls back to heuristic line count for bare environments.

### Gate 2 — CFD Convergence

| Metric | Limit | Source |
|--------|-------|--------|
| Final residuals (all) | < 1e-4 | Standard CFD convergence |
| Force balance error | < 5% | Conservation check |

Parses OpenFOAM `log.simpleFoam` for residual lines.  Also detects hard
divergence markers (`FOAM FATAL ERROR`, `Floating point exception`, etc.).

## Format Converters

### Converter 1: Gmsh .msh → OpenFOAM polyMesh

```python
from convert_gmsh_to_openfoam import convert

result = convert(
    msh_path="mesh.msh",
    case_dir="/path/to/of_case",
    patch_map={
        "inlet": "patch",
        "outlet": "patch",
        "cylinder": "wall",
        "top": "symmetryPlane",
    }
)
# result["passed"] == True when polyMesh files are written
```

Priority: `gmshToFoam` CLI (OpenFOAM) → `meshio` Python → stub bypass.

### Converter 2: OpenFOAM forces → OrcaFlex load CSV

```python
from convert_openfoam_to_orcaflex import convert

result = convert(
    forces_path="postProcessing/forces/0/force.dat",
    output_csv="loads.csv",
    scale_factor=1.0,   # model→full scale if needed
    time_step=0.1,      # re-sample to uniform dt
)
# result["row_count"] = number of time steps written
```

Reads bracketed-tuple OpenFOAM forces format (pressure + viscous components).
Writes six-column CSV: `Time, Fx, Fy, Fz, Mx, My, Mz`.

## Stub Mode Details

When `--stub-mode` is set or `PIPELINE_STUB_MODE=1`:

| Stub | Method | Outputs |
|------|--------|---------|
| `stub_gmsh.py` | Structured hex grid, cylinder void removed | Valid MSH2 file |
| `stub_openfoam.py` | Analytical Cd=1.0 drag, decaying residuals | log.simpleFoam + force.dat |
| `stub_orcaflex.py` | Fixed-free cantilever beam theory | deflection [m], tension [N] |

Analytical reference for cylinder drag:
```
F_drag = 0.5 * rho * U^2 * D * L * Cd
       = 0.5 * 1025 * 1.5^2 * 1.0 * 5.0 * 1.0
       = 5765.6 N   (for D=1m, L=5m, U=1.5m/s)
```

## Real Mode Requirements

| Solver | Installation | Check |
|--------|-------------|-------|
| Gmsh | `pip install gmsh` | `python3 -c "import gmsh"` |
| OpenFOAM v2312 | ESI apt repo | `source /usr/lib/openfoam/openfoam2312/etc/bashrc` |
| OrcFxAPI | Orcina license | `python3 -c "import OrcFxAPI"` |

The pipeline auto-detects availability and falls back to stubs gracefully.

## Agent Usage Pattern

An agent can invoke the full pipeline with a single structured call:

```python
# Agent invocation (WRK item execution pattern)
import subprocess, json, sys

result = subprocess.run(
    [
        sys.executable,
        "scripts/pipelines/gmsh_openfoam_orcaflex.py",
        "--diameter", "1.0",
        "--length", "5.0",
        "--velocity", "1.5",
        "--work-dir", "/tmp/wrk_run",
        "--stub-mode",    # remove when solvers are installed
        "--json",
    ],
    capture_output=True, text=True
)

data = json.loads(result.stdout.split("\n{")[1])  # strip pipeline print
# OR: read /tmp/wrk_run/pipeline_results.json

assert data["passed"], f"Pipeline failed: {data['issues']}"
drag = data["summary"]["drag_force_N"]
deflection = data["summary"]["max_deflection_m"]
```

## Error Propagation Map

| Stage | Common Failure | Effect | Detection |
|-------|---------------|--------|-----------|
| Gmsh | Invalid geometry params | Empty .msh | Gate 1: cell_count = 0 |
| Gmsh | Mesh too coarse | High skewness | Gate 1: max_skewness >= 4.0 |
| gmshToFoam | OpenFOAM not sourced | Conversion fails | Stub bypass in stub mode |
| OpenFOAM | Divergence | Residuals >> 1e-4 | Gate 2: converged=False |
| OpenFOAM | Missing forces function | No force.dat | Gate 2: forces file not found |
| OrcaFlex | No license | ImportError | Auto-fallback to stub |
| OrcaFlex | Negative tension | Compression in mooring | Check max_tension_N >= 0 |

## Related Skills

- [cfd-pipeline](../cfd-pipeline/SKILL.md) — Gmsh→OpenFOAM→ParaView workflow
- [hydrodynamic-pipeline](../hydrodynamic-pipeline/SKILL.md) — OrcaWave→OrcaFlex
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) — Gmsh mesh generation
- [openfoam](../../cfd/openfoam/SKILL.md) — OpenFOAM solver interface
- [orcaflex-modeling](../../marine-offshore/orcaflex-modeling/SKILL.md) — OrcaFlex API

---

## Version History

- **1.0.0** (2026-02-24): Initial multi-physics pipeline skill (WRK-380).
  40/40 tests passing in stub mode. All acceptance criteria met.
