---
name: freecad-automation-200-2026-03-16
description: 'Sub-skill of freecad-automation: [2.0.0] - 2026-03-16 (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# [2.0.0] - 2026-03-16 (+1)

## [2.0.0] - 2026-03-16


**Added:**
- Parametric hull NURBS generation (`FreeCADHullGenerator`) with scipy fallback
- Analytical hydrostatics via section integration (`HullHydrostatics`)
- CalculiX FEM chain: INP writer, result parser, end-to-end pipeline (`FEMChain`)
- STEP import and INP export in gmsh meshing module
- Design table batch studies with multiprocessing parallelism (`DesignTable`)
- Manifold validation for hull surfaces (`ManifoldChecker`)
- Full round-trip: HullProfile → NURBS → STEP → gmsh → INP → CalculiX

## [1.0.0] - 2026-01-07


**Added:**
- Initial version metadata and dependency management
- Semantic versioning support
- Compatibility information for Python 3.10-3.13

**Changed:**
- Enhanced skill documentation structure
