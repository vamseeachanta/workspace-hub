---
name: gmsh-openfoam-orcaflex-gate-1-mesh-quality
description: "Sub-skill of gmsh-openfoam-orcaflex: Gate 1 \u2014 Mesh Quality (+1)."
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Gate 1 — Mesh Quality (+1)

## Gate 1 — Mesh Quality


| Metric | Limit | Source |
|--------|-------|--------|
| Max skewness | < 4.0 | OpenFOAM checkMesh default |
| Max non-orthogonality | < 70 deg | OpenFOAM checkMesh default |
| Cell count | >= 100 | Pipeline minimum |

Gate uses `checkMesh` when OpenFOAM is sourced; falls back to gmsh Python API
quality metric; falls back to heuristic line count for bare environments.


## Gate 2 — CFD Convergence


| Metric | Limit | Source |
|--------|-------|--------|
| Final residuals (all) | < 1e-4 | Standard CFD convergence |
| Force balance error | < 5% | Conservation check |

Parses OpenFOAM `log.simpleFoam` for residual lines.  Also detects hard
divergence markers (`FOAM FATAL ERROR`, `Floating point exception`, etc.).
