---
name: gmsh-meshing
version: 1.0.0
category: engineering
description: "gmsh Meshing Skill \u2014 CLI, .geo scripting, Python API, and solver\
  \ integration"
tags:
- gmsh
- mesh
- meshing
- cad
- geometry
- bem
- fem
- marine
- hydrodynamic
- opencascade
platforms:
- windows
- linux
- macos
invocation: gmsh-meshing
depends_on:
- cad-mesh-generation
- mesh-utilities
capabilities: []
requires: []
see_also:
- gmsh-meshing-executable
- gmsh-meshing-batch-meshing
- gmsh-meshing-geometry-primitives
- gmsh-meshing-initialization-and-model-management
- gmsh-meshing-box-barge-surface-mesh-bem
- gmsh-meshing-export-to-aqwa-dat-format
- gmsh-meshing-quality-metrics
scripts_exempt: true
---

# Gmsh Meshing

## When to Use This Skill

Use this skill when you need to:
- Generate surface panel meshes for BEM hydrodynamic solvers
- Create structured (transfinite) or unstructured meshes
- Script parametric geometries with .geo or Python API
- Perform boolean/CSG operations via OpenCASCADE kernel
- Import and remesh STEP, STL, or IGES geometry
- Control mesh density with size fields (distance, threshold, background)
- Export meshes to AQWA (.DAT), WAMIT (.GDF), Nemoh, or general formats (MSH, STL, VTK, UNV)
- Batch-generate meshes from the command line

**Cross-references:**
- GDF/CDB export code → `skills/data/scientific/cad-mesh-generation/SKILL.md`
- Mesh inspection/conversion → `skills/engineering/marine-offshore/mesh-utilities/SKILL.md`

## Resources

### Online Documentation

- **Official docs**: https://gmsh.info/doc/texinfo/gmsh.html
- **Python API reference**: https://gmsh.info/doc/texinfo/gmsh.html#Gmsh-API
- **Tutorials**: https://gmsh.info/#Tutorials
- **Source repository**: https://gitlab.onelab.info/gmsh/gmsh
### Local Installation

- **Executable**: `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe`
- **Tutorials (.geo)**: `D:\software\gmsh\gmsh-4.15.0-Windows64\tutorials\t1.geo` through `t21.geo`
- **Python tutorials**: `D:\software\gmsh\gmsh-4.15.0-Windows64\tutorials\python\`
- **API examples**: `D:\software\gmsh\gmsh-4.15.0-Windows64\examples\api\`
- **Boolean examples**: `D:\software\gmsh\gmsh-4.15.0-Windows64\examples\boolean\`
### Tutorial Index

See `assets/gmsh-reference.md` for complete tutorial descriptions and CLI options reference.
### Related Skills

- `skills/data/scientific/cad-mesh-generation/SKILL.md` — FreeCAD + gmsh workflows, GDF/CDB export
- `skills/engineering/marine-offshore/mesh-utilities/SKILL.md` — mesh inspection, conversion, quality checks
- `skills/engineering/cad/cad-engineering/SKILL.md` — general CAD engineering
- `skills/engineering/cad/freecad-automation/SKILL.md` — FreeCAD automation

## Sub-Skills

- [Common Issues (+1)](common-issues/SKILL.md)

## Sub-Skills

- [Executable (+2)](executable/SKILL.md)
- [Batch Meshing (+2)](batch-meshing/SKILL.md)
- [Geometry Primitives (+5)](geometry-primitives/SKILL.md)
- [Initialization and Model Management (+6)](initialization-and-model-management/SKILL.md)
- [Box Barge Surface Mesh (BEM) (+4)](box-barge-surface-mesh-bem/SKILL.md)
- [Export to AQWA (.DAT Format) (+4)](export-to-aqwa-dat-format/SKILL.md)
- [Quality Metrics (+1)](quality-metrics/SKILL.md)
