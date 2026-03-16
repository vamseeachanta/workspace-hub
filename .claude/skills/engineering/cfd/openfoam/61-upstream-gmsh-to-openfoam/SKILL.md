---
name: openfoam-61-upstream-gmsh-to-openfoam
description: 'Sub-skill of openfoam: 6.1 Upstream: Gmsh to OpenFOAM (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 6.1 Upstream: Gmsh to OpenFOAM (+3)

## 6.1 Upstream: Gmsh to OpenFOAM


```bash
# Convert Gmsh mesh to OpenFOAM format
gmshToFoam mesh.msh
# Check and fix orientation
checkMesh
# If needed: renumber for performance
renumberMesh -overwrite
```


## 6.2 Upstream: FreeCAD/CAD to OpenFOAM


```bash
# Export STL from FreeCAD/CAD
# Place STL in constant/triSurface/
# Use snappyHexMesh for mesh generation around geometry
```


## 6.3 Downstream: OpenFOAM to ParaView


```bash
foamToVTK -latestTime
# Open VTK/case.vtm in ParaView
# Or open the case directly: paraFoam (if paraview-openfoam plugin installed)
```


## 6.4 Python Integration (meshio)


```python
import meshio
# Read OpenFOAM mesh
mesh = meshio.read("constant/polyMesh")
# Convert to other formats
meshio.write("output.vtu", mesh)
```
