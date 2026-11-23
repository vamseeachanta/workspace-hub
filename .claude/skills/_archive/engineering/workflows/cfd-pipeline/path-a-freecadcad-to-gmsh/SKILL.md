---
name: cfd-pipeline-path-a-freecadcad-to-gmsh
description: 'Sub-skill of cfd-pipeline: Path A: FreeCAD/CAD to Gmsh (+3).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Path A: FreeCAD/CAD to Gmsh (+3)

## Path A: FreeCAD/CAD to Gmsh


```bash
# 1. Export from FreeCAD to STEP/BREP
freecadcmd -c "
import FreeCAD, Part
doc = FreeCAD.openDocument('geometry.FCStd')
Part.export(doc.Objects, 'geometry.step')
"

# 2. Mesh with Gmsh
gmsh geometry.step -3 -format msh2 -o mesh.msh \
  -clmin 0.01 -clmax 0.5 \
  -algo del3d
```


## Gmsh to OpenFOAM Conversion


```bash
# Convert Gmsh mesh to OpenFOAM format
gmshToFoam mesh.msh

# Fix boundary patches (Gmsh exports generic names)
# Edit constant/polyMesh/boundary to set correct patch types
```

```python
# Automated Gmsh-to-OpenFOAM boundary patch fix
import re
from pathlib import Path

def fix_boundary_patches(case_dir, patch_map):
    """Fix boundary patch types after gmshToFoam conversion.

    Args:
        case_dir: OpenFOAM case directory
        patch_map: dict of {patch_name: patch_type}
            e.g. {'inlet': 'patch', 'outlet': 'patch', 'walls': 'wall'}
    """
    boundary_file = Path(case_dir) / 'constant' / 'polyMesh' / 'boundary'
    content = boundary_file.read_text()

    for name, ptype in patch_map.items():
        # Replace patch type for named patch
        pattern = rf'({name}\s*\{{[^}}]*type\s+)\w+'
        content = re.sub(pattern, rf'\g<1>{ptype}', content)

    boundary_file.write_text(content)
```


## Path B: CAD to snappyHexMesh (Complex Geometry)


```bash
# 1. Export STL from CAD (FreeCAD or external)
# Ensure STL is watertight and in meters

# 2. Create background mesh with blockMesh
blockMesh

# 3. Run snappyHexMesh
snappyHexMesh -overwrite

# Key files needed:
# - system/blockMeshDict     (background mesh)
# - system/snappyHexMeshDict (refinement + snapping)
# - constant/triSurface/geometry.stl
```


## Validation: Geometry to Mesh


```python
def validate_geometry_to_mesh(stl_path, mesh_dir):
    """Validate the geometry-to-mesh conversion."""
    import subprocess
    checks = {"passed": True, "issues": []}

    # Check STL is readable
    import os
    if not os.path.exists(stl_path):
        checks["issues"].append(f"STL not found: {stl_path}")
        checks["passed"] = False
        return checks

    stl_size = os.path.getsize(stl_path)
    if stl_size < 100:
        checks["issues"].append(f"STL suspiciously small: {stl_size} bytes")
        checks["passed"] = False

    # Check OpenFOAM mesh
    polymesh = os.path.join(mesh_dir, 'constant', 'polyMesh', 'points')
    if not os.path.exists(polymesh):
        checks["issues"].append("No polyMesh/points — mesh conversion failed")
        checks["passed"] = False
        return checks

    # Run checkMesh
    result = subprocess.run(
        ['checkMesh', '-case', mesh_dir],
        capture_output=True, text=True
    )
    if 'FAILED' in result.stdout:
        checks["issues"].append("checkMesh reports failures")
        checks["passed"] = False

    # Extract mesh stats
    import re
    cells_match = re.search(r'cells:\s+(\d+)', result.stdout)
    if cells_match:
        checks["cells"] = int(cells_match.group(1))

    return checks
```
