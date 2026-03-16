---
name: blender-interface
description: "AI interface skill for Blender 3D \u2014 headless CLI execution, Python\
  \ bpy API, mesh import/export, rendering, and integration with engineering analysis\
  \ workflows."
version: 1.1.0
updated: 2026-02-24
category: engineering
triggers:
- Blender automation
- Blender Python
- bpy scripting
- 3D visualization
- Blender render
- mesh to Blender
- OrcaFlex visualization Blender
- headless Blender
- Blender CLI
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also:
- blender-interface-scene-setup-via-python-script
- blender-interface-cli-headless-execution
- blender-interface-render-output-locations
- blender-interface-common-failures
- blender-interface-mesh-quality-checks
- blender-interface-orcaflex-results-to-blender-visualization
tags: []
scripts_exempt: true
---

# Blender Interface

## Related Skills

- [freecad-automation](../freecad-automation/SKILL.md) - Parametric CAD geometry
- [gmsh-meshing](../gmsh-meshing/SKILL.md) - Mesh generation for analysis
- [paraview-interface](../../cfd/paraview/SKILL.md) - Scientific visualization

## References

- Blender Python API: https://docs.blender.org/api/current/
- Blender CLI Reference: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html

---

## Version History

- **1.1.0** (2026-02-24): Validated against Blender 5.0.1. Added 5.x migration column (EEVEE enum revert, use_nodes deprecation), version-safe render config, 2 new failure diagnosis entries.
- **1.0.0** (2026-02-23): Initial full interface skill covering CLI execution, bpy API, 3.x/4.x migration, rendering, mesh validation, and engineering integration.

## Sub-Skills

- [Scene Setup via Python Script (+5)](scene-setup-via-python-script/SKILL.md)
- [CLI Headless Execution (+3)](cli-headless-execution/SKILL.md)
- [Render Output Locations (+3)](render-output-locations/SKILL.md)
- [Common Failures (+2)](common-failures/SKILL.md)
- [Mesh Quality Checks (+2)](mesh-quality-checks/SKILL.md)
- [OrcaFlex Results to Blender Visualization (+2)](orcaflex-results-to-blender-visualization/SKILL.md)
