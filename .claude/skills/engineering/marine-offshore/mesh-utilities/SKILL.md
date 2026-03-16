---
name: mesh-utilities
version: 1.0.0
description: Quick mesh inspection, conversion, quality checks, and coarsening for
  hydrodynamic solvers
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
see_also:
- mesh-utilities-1-quick-mesh-inspection
- mesh-utilities-batch-quality-check
- mesh-utilities-pre-solver-checklist
- mesh-utilities-cli-usage
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
- **orcaflex-specialist** - OrcaFlex integration
- **gmsh-meshing** - Advanced mesh generation

---

**Use this skill for quick mesh checks before running expensive solver analyses!**

## Sub-Skills

- [Troubleshooting](troubleshooting/SKILL.md)

## Sub-Skills

- [Quick Reference](quick-reference/SKILL.md)

## Sub-Skills

- [1. Quick Mesh Inspection (+5)](1-quick-mesh-inspection/SKILL.md)
- [Batch Quality Check (+1)](batch-quality-check/SKILL.md)
- [Pre-Solver Checklist](pre-solver-checklist/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
