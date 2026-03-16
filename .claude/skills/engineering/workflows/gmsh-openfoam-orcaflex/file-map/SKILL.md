---
name: gmsh-openfoam-orcaflex-file-map
description: 'Sub-skill of gmsh-openfoam-orcaflex: File Map.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# File Map

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
