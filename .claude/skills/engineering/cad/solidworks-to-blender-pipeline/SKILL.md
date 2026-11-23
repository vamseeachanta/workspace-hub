---
name: solidworks-to-blender-pipeline
description: Use when converting SolidWorks .sldprt/.sldasm geometry to Blender for rendering, animation, or visualization, including questions about STEP export settings, FreeCAD as a bridge, or which mesh format (STL/OBJ/GLTF) to choose.
type: reference
version: 1.0.0
updated: 2026-05-10
category: engineering
triggers:
  - SolidWorks to Blender
  - .sldprt import
  - .sldasm import
  - STEP to Blender
  - IGES to Blender
  - CAD to render pipeline
  - FreeCAD bridge for Blender
  - mechanical CAD visualization
  - GLTF from CAD
  - SolidWorks export settings
  - SolidWorks STL
  - Parasolid export
capabilities:
  - reference
requires: []
tags:
  - cad
  - blender
  - solidworks
  - freecad
  - step
  - gltf
scripts_exempt: true
---

# SolidWorks → Blender Pipeline

## Overview

No FOSS tool natively parses `.sldprt` / `.sldasm` — Dassault keeps the format proprietary. The reliable pipeline goes through an interchange format (**STEP** preferred, IGES fallback) and optionally **FreeCAD** as a cleanup bridge before Blender.

Core principle: **STEP is the contract.** Treat the SolidWorks-side STEP export as the only durable surface — everything downstream re-derives from it.

## When to Use

- Importing mechanical CAD into Blender for rendering, animation, or marketing visuals
- Choosing between STL / OBJ / GLTF for a Blender-bound asset
- Deciding whether to add FreeCAD as an intermediate (yes, if geometry needs cleanup or assemblies need to be preserved)
- Picking SolidWorks STEP export flags
- Evaluating direct `.sldprt` readers (short answer: only commercial/partial — Fusion personal, MoI3D, CAD Exchanger, Okino PolyTrans)

Don't use when:
- You only need a print-ready mesh → go straight to STL (no Blender)
- You're staying inside the FreeCAD ecosystem → see `../freecad-automation/SKILL.md`
- You're rendering pre-existing Blender scenes → see `../blender/SKILL.md`

## Decision matrix — pipeline by use case

| Use case | Pipeline | Why |
|---|---|---|
| Rendering / animation | `SW → STEP → FreeCAD → GLTF → Blender` | GLTF preserves hierarchy + materials |
| 3D printing | `SW → STL` | Mesh-only, no need for Blender |
| Game assets | `SW → STEP → Blender (retopo)` | Quads needed, original solids discarded |
| Fully FOSS workflow | `FreeCAD + Blender` (no SW step) | Avoid the proprietary format entirely |
| Quick geometry check / repair | `SW → STEP → CAD Assistant` | Lightweight viewer, exports STL/OBJ |

## Recommended export settings (SolidWorks side)

Export as **STEP AP242 Binary** with the following enabled:
- Curves
- Assembly structure
- Colors

Rationale: AP242 is the modern PMI-bearing flavor; binary halves file size vs ASCII; the three flags above are commonly off by default and silently drop information Blender can otherwise show.

## FreeCAD bridge (when to use it)

Add FreeCAD between SolidWorks and Blender when any of:
- Assembly hierarchy must survive (FreeCAD preserves it better than Blender's STEP importer)
- Topology needs cleaning before tessellation
- You want fine control over mesh density per body
- You need a Python automation step (FreeCAD's `Part` + `Mesh` modules)

Inside FreeCAD: `Mesh → Mesh from shape → Fine tessellation → Export GLTF`.

GLTF beats STL for Blender because it preserves hierarchy, materials, and is smaller. STL still wins when the next consumer is a 3D printer or analysis mesher.

## Tool inventory

**Open-source (recommended):**
- **FreeCAD** — bridge of choice; cross-link `../freecad-automation/SKILL.md`
- **Blender + add-ons** — STEPper, CAD Sketcher, BlenderBIM, OCC/STEP importers. Note: imported solids become polygon meshes; assemblies may flatten; constraints/features/history are lost
- **CAD Assistant** — lightweight STEP viewer + STL/OBJ exporter (not a full editor)

**Commercial-ish (the only paths that read `.sldprt` more directly):**
- Autodesk Fusion personal edition
- MoI3D
- CAD Exchanger
- Okino PolyTrans

**The open-source reality:** even the FOSS tools above rely on STEP / Parasolid export from a SolidWorks seat. There is no robust direct-read path; if you don't have a SolidWorks license to export from, you need someone who does.

## Common mistakes

| Mistake | Fix |
|---|---|
| Exporting STEP AP203 by default | Switch to AP242 — AP203 drops colors and PMI |
| Choosing STL for a Blender render | Use GLTF; STL is mesh-only and strips materials |
| Skipping FreeCAD when assembly hierarchy matters | Run STEP through FreeCAD first — Blender flattens assemblies more aggressively |
| Tessellating coarsely | FreeCAD's "fine" tessellation is the floor for renders; bump deviation lower for hero shots |
| Treating direct `.sldprt` readers as drop-in | All are partial — geometry yes, features/history no |

## Related skills

- [blender](../blender/SKILL.md) — once geometry is in Blender, the bpy/CLI side
- [freecad-automation](../freecad-automation/SKILL.md) — scripting the FreeCAD intermediate step
- [gmsh-meshing](../gmsh-meshing/SKILL.md) — when the destination is FEM/CFD, not render
- [pyvista-3d](../pyvista-3d/SKILL.md) — alternative visualization path without Blender

## References

- FreeCAD: https://www.freecad.org/
- Blender: https://www.blender.org/
- STEP AP242 overview: https://www.iso.org/standard/66654.html

## Version history

- **1.0.0** (2026-05-10): Initial reference. Source: external ChatGPT consult on SolidWorks→Blender FOSS workflow; cross-referenced against existing `blender` and `freecad-automation` skills.
