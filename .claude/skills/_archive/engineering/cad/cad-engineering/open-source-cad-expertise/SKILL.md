---
name: cad-engineering-open-source-cad-expertise
description: 'Sub-skill of cad-engineering: Open-Source CAD Expertise (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Open-Source CAD Expertise (+3)

## Open-Source CAD Expertise


| Software | Capabilities |
|----------|-------------|
| **FreeCAD** | Parametric 3D modeling, Python scripting, workbench customization |
| **LibreCAD** | 2D drafting, DXF/DWG handling, command-line operations |
| **OpenSCAD** | Programmatic 3D modeling, CSG operations, parametric design |
| **QCAD** | Professional 2D CAD, scripting interface, batch processing |
| **BRL-CAD** | Solid modeling, ray-tracing, geometric analysis |
| **Blender** | CAD integration, mesh to solid conversion, technical visualization |
| **KiCAD** | PCB design, electrical schematics, 3D board visualization |

## Proprietary CAD Knowledge


| Software | Capabilities |
|----------|-------------|
| **AutoCAD** | Full command set, AutoLISP/VBA automation, custom tools |
| **SolidWorks** | Feature-based modeling, API programming, PDM integration |
| **CATIA** | V5/V6 platforms, complex surfaces, PLM workflows |
| **Inventor** | Parametric design, iLogic rules, Vault integration |
| **Fusion 360** | Cloud collaboration, generative design, CAM integration |
| **Creo/Pro-E** | Advanced assembly, mechanism design |
| **NX** | High-end manufacturing, synchronous technology |

## File Format Expertise


| Category | Formats |
|----------|---------|
| **Native** | DWG, DXF, DGN, IGES, STEP, STL, SAT, Parasolid |
| **Exchange** | IFC, COLLADA, OBJ, FBX, 3DS, VRML, X3D |
| **Documentation** | PDF, SVG, EPS, DWF, 3D PDF |

## Delegation Capability


This specialist agent delegates to software-specific agents:

```yaml
delegation:
  software_specific_agents:
    freecad:
      path: agents/freecad
      capabilities:
        - parametric_modeling
        - assembly_design

*See sub-skills for full details.*
