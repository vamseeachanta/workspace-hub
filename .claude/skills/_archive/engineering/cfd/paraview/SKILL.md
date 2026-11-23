---
name: paraview-interface
description: "AI interface skill for ParaView scientific visualization \u2014 pvpython/pvbatch\
  \ CLI execution, paraview.simple API, filter pipelines, OpenFOAM integration, and\
  \ automated image/data export."
version: 1.1.0
updated: 2026-02-24
category: engineering
triggers:
- ParaView automation
- pvpython
- pvbatch
- ParaView Python
- OpenFOAM visualization
- VTK visualization
- CFD post-processing
- paraview.simple
- ParaView filter
- ParaView screenshot
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also:
- paraview-interface-python-script-structure-paraviewsimple
- paraview-interface-cli-execution
- paraview-interface-save-screenshots
- paraview-interface-common-failures
- paraview-interface-verify-data-range
- paraview-interface-openfoam-to-paraview-pipeline
tags: []
scripts_exempt: true
---

# Paraview Interface

## Related Skills

- [openfoam](../openfoam/SKILL.md) - OpenFOAM CFD solver interface
- [blender-interface](../../cad/blender/SKILL.md) - 3D rendering and visualization
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) - Mesh generation

## References

- ParaView Python API: https://kitware.github.io/paraview-docs/latest/python/
- ParaView Catalyst: https://www.paraview.org/in-situ/

---

## Version History

- **1.1.0** (2026-02-24): Validated against VTK 9.6.0 (35/35 checks). Added ParaView 5.11 crash diagnosis for Ubuntu 24.04 + NVIDIA 580. All filter operations, CSV parsing, and data flow verified.
- **1.0.0** (2026-02-23): Initial full interface skill covering pvpython/pvbatch execution, paraview.simple API, filter pipelines, OpenFOAM integration, and validation.

## Sub-Skills

- [Python Script Structure (paraview.simple) (+5)](python-script-structure-paraviewsimple/SKILL.md)
- [CLI Execution (+3)](cli-execution/SKILL.md)
- [Save Screenshots (+5)](save-screenshots/SKILL.md)
- [Common Failures (+1)](common-failures/SKILL.md)
- [Verify Data Range (+2)](verify-data-range/SKILL.md)
- [OpenFOAM to ParaView Pipeline (+2)](openfoam-to-paraview-pipeline/SKILL.md)
