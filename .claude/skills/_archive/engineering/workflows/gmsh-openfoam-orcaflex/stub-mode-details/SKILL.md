---
name: gmsh-openfoam-orcaflex-stub-mode-details
description: 'Sub-skill of gmsh-openfoam-orcaflex: Stub Mode Details.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Stub Mode Details

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
