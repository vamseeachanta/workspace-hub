---
name: mesh-utilities
version: 1.0.0
description: Quick mesh inspection, conversion, quality checks, and coarsening for
  hydrodynamic solvers
type: reference
author: workspace-hub
category: engineering-utilities
tags:
- mesh
- gdf
- dat
- stl
- bem
- panel-mesh
- quality
- coarsening
- aqwa
- orcawave
- bemrosetta
platforms:
- engineering
invocation: /mesh
capabilities: []
requires: []
---

# Mesh Utilities

## When to Use This Skill

Use mesh utilities when you need to:
- **Quick inspect** - View mesh statistics (panels, vertices, bounding box) before running solvers
- **Format conversion** - Convert between GDF (OrcaWave/WAMIT), DAT (AQWA/NEMOH), and STL
- **Quality validation** - Check watertightness, normals, aspect ratios, panel counts
- **Mesh coarsening** - Reduce panel count for faster preliminary runs
- **Pre-solver checks** - Validate mesh suitability for specific solvers (AQWA, OrcaWave, BEMRosetta)

## Related Skills

- **hydrodynamic-analysis** - BEM theory, RAOs, added mass/damping
- **orcaflex/specialist** - OrcaFlex integration
- **gmsh-meshing** - Advanced mesh generation

---

**Use this skill for quick mesh checks before running expensive solver analyses!**

## Sub-Skills

- Troubleshooting

## Sub-Skills

- Quick Reference

## Sub-Skills

- 1. Quick Mesh Inspection (+5)
- Batch Quality Check (+1)
- Pre-Solver Checklist
- CLI Usage
