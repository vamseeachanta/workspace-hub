---
name: cfd-pipeline-pipeline-overview
description: 'Sub-skill of cfd-pipeline: Pipeline Overview.'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Pipeline Overview

## Pipeline Overview


```
FreeCAD / External CAD          Gmsh / blockMesh / snappyHexMesh
   (geometry)          ────►        (meshing)
       │                                │
   .step/.stl/.brep                 OpenFOAM polyMesh/
                                        │
                                        ▼
                                   OpenFOAM Solver
                                   (SIMPLE/PIMPLE)
                                        │
                                  time directories/
                                        │
                              ┌─────────┴──────────┐
                              ▼                    ▼
                          ParaView             Blender
                       (analysis viz)      (presentation viz)
```
