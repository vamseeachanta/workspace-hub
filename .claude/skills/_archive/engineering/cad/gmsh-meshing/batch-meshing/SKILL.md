---
name: gmsh-meshing-batch-meshing
description: 'Sub-skill of gmsh-meshing: Batch Meshing (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Batch Meshing (+2)

## Batch Meshing


```bash
# Generate 2D surface mesh and save
gmsh model.geo -2 -o output.msh

# Generate 3D volume mesh
gmsh model.geo -3 -o output.msh

# Specify output format
gmsh model.geo -2 -format msh22 -o output.msh


*See sub-skills for full details.*

## Format Conversion


```bash
# Convert MSH to STL
gmsh input.msh -o output.stl

# Convert STEP to mesh
gmsh input.step -2 -o output.msh

# Convert to MSH v2.2 (for BEM tools)
gmsh input.msh -format msh22 -o output.msh

# Convert with binary format
gmsh input.msh -bin -convert output.msh
```

## Key CLI Flags


| Flag | Description |
|------|-------------|
| `-0` | Output model only (no mesh), then exit |
| `-1`, `-2`, `-3` | Generate 1D/2D/3D mesh |
| `-format <fmt>` | Output format (msh2, msh22, stl, vtk, etc.) |
| `-o <file>` | Output file path |
| `-bin` | Binary output |
| `-clscale <f>` | Global mesh size factor |
| `-clmin <f>` | Minimum element size |
| `-clmax <f>` | Maximum element size |

*See sub-skills for full details.*
