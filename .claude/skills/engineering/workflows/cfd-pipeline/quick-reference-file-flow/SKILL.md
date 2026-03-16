---
name: cfd-pipeline-quick-reference-file-flow
description: 'Sub-skill of cfd-pipeline: Quick Reference: File Flow.'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Quick Reference: File Flow

## Quick Reference: File Flow


```
FreeCAD (.FCStd) ──export──► .step/.stl
                                  │
            gmsh (.geo) ──mesh──► .msh ──gmshToFoam──► polyMesh/
                                                           │
            blockMesh ──────────────────────────────► polyMesh/
                                                           │
                                  snappyHexMesh ───────► polyMesh/
                                                           │
                              OpenFOAM solver ──────► time dirs (0.1/, 0.2/, ...)
                                                           │
                              foamToVTK ────────────► VTK/*.vtk
                                                           │
                    ┌──────────────────────────────────────┤
                    ▼                                      ▼
              ParaView (.foam)                    Blender (.stl via meshio)
              ├── screenshots                     ├── high-quality renders
              ├── CSV line probes                 └── animation
              └── animations
```
