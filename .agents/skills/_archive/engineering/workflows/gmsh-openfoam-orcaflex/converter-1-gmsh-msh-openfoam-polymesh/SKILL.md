---
name: gmsh-openfoam-orcaflex-converter-1-gmsh-msh-openfoam-polymesh
description: "Sub-skill of gmsh-openfoam-orcaflex: Converter 1: Gmsh .msh \u2192 OpenFOAM\
  \ polyMesh (+1)."
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Converter 1: Gmsh .msh → OpenFOAM polyMesh (+1)

## Converter 1: Gmsh .msh → OpenFOAM polyMesh


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


## Converter 2: OpenFOAM forces → OrcaFlex load CSV


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
