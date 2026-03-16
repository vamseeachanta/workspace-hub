---
name: gmsh-openfoam-orcaflex-error-propagation-map
description: 'Sub-skill of gmsh-openfoam-orcaflex: Error Propagation Map.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Propagation Map

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
