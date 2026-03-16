---
name: gmsh-meshing-executable
description: 'Sub-skill of gmsh-meshing: Executable (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Executable (+2)

## Executable


| Platform | Path |
|----------|------|
| Windows (local) | `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe` |
| Linux/macOS | `gmsh` (install via package manager or `pip install gmsh`) |
| Python module | `pip install gmsh` (provides `import gmsh`) |

## Supported Output Formats


| Format | Extension | Use Case |
|--------|-----------|----------|
| MSH v2.2 | `.msh` | BEM tools (BEMRosetta, Nemoh) |
| MSH v4.1 | `.msh` | Default, full feature support |
| STL | `.stl` | Visualization, 3D printing |
| VTK | `.vtk` | ParaView visualization |
| UNV | `.unv` | Salome, Code_Aster |
| Nastran BDF | `.bdf` | ANSYS, Nastran FEA |
| Abaqus INP | `.inp` | Abaqus FEA |
| Fluent DAT | `.dat` | Fluent CFD |
| CGNS | `.cgns` | CFD interoperability |
| MED | `.med` | Salome/Code_Aster |
| SU2 | `.su2` | SU2 CFD |
| OFF | `.off` | Geometry processing |

## Mesh Algorithms


| ID | Name | Dimension | Description |
|----|------|-----------|-------------|
| 1 | MeshAdapt | 2D | Adaptive, good for complex geometries |
| 5 | Delaunay | 2D | Default 2D, robust general purpose |
| 6 | Frontal-Delaunay | 2D | Better quality triangles |
| 8 | DelQuad | 2D | Delaunay for quads (recombine) |
| 9 | Packing of Parallelograms | 2D | Structured-like quad meshing |
| 1 | Delaunay | 3D | Default 3D tetrahedral |
| 4 | Frontal | 3D | Better quality tets |
| 7 | MMG3D | 3D | Remeshing with MMG |
| 10 | HXT | 3D | Parallel Delaunay (fast) |
