---
name: gmsh-openfoam-orcaflex-pipeline-architecture
description: 'Sub-skill of gmsh-openfoam-orcaflex: Pipeline Architecture.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Pipeline Architecture

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
