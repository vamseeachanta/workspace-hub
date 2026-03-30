---
name: hydrodynamic-pipeline-pipeline-overview
description: 'Sub-skill of hydrodynamic-pipeline: Pipeline Overview.'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Pipeline Overview

## Pipeline Overview


```
FreeCAD / Gmsh                    OrcaWave / AQWA
  (panel mesh)        ────►     (diffraction/radiation)
      │                                  │
  .gdf / .dat mesh                  RAOs, added mass,
                                    damping, QTFs
                                         │
                                         ▼
                                    OrcaFlex
                                (coupled dynamic analysis)
                                         │
                                    .sim results
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                         OrcaFlex Post          ParaView/Blender
                        (statistics)           (visualization)
```
