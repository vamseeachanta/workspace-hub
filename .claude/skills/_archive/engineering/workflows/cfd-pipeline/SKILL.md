---
name: cfd-pipeline
description: "Cross-program workflow for CFD analysis \u2014 geometry (FreeCAD/Gmsh)\
  \ to meshing (Gmsh/snappyHexMesh) to solving (OpenFOAM) to visualization (ParaView/Blender).\
  \ Covers data flow, format conversion, and validation between programs."
version: 1.0.1
updated: 2026-02-24
category: engineering
triggers:
- CFD pipeline
- CFD workflow
- geometry to mesh to solve
- OpenFOAM workflow
- end-to-end CFD
- meshing to solving
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires:
- gmsh-meshing
- openfoam
- paraview-interface
see_also:
- cfd-pipeline-pipeline-overview
- cfd-pipeline-path-a-freecadcad-to-gmsh
- cfd-pipeline-openfoam-case-setup-from-mesh
- cfd-pipeline-openfoam-to-paraview
- cfd-pipeline-validation-points-in-the-pipeline
- cfd-pipeline-quick-reference-file-flow
tags: []
scripts_exempt: true
---

# Cfd Pipeline

## Related Skills

- [openfoam](../../cfd/openfoam/SKILL.md) - OpenFOAM solver interface
- [paraview-interface](../../cfd/paraview/SKILL.md) - ParaView visualization
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) - Mesh generation
- [freecad-automation](../../cad/freecad-automation/SKILL.md) - CAD geometry
- [blender-interface](../../cad/blender/SKILL.md) - 3D rendering

---

## Version History

- **1.0.1** (2026-02-24): Fixed pvbatch -c inline flag (not supported) → script file pattern (validated 148/151→151/151)
- **1.0.0** (2026-02-23): Initial cross-program workflow skill for CFD pipeline (WRK-372 Phase 4).

## Sub-Skills

- [Pipeline Overview](pipeline-overview/SKILL.md)
- [Path A: FreeCAD/CAD to Gmsh (+3)](path-a-freecadcad-to-gmsh/SKILL.md)
- [OpenFOAM Case Setup from Mesh (+2)](openfoam-case-setup-from-mesh/SKILL.md)
- [OpenFOAM to ParaView (+1)](openfoam-to-paraview/SKILL.md)
- [Validation Points in the Pipeline (+1)](validation-points-in-the-pipeline/SKILL.md)
- [Quick Reference: File Flow](quick-reference-file-flow/SKILL.md)
