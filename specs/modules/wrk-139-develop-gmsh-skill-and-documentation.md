---
title: "WRK-139: Develop gmsh Skill and Documentation"
description: Create a dedicated gmsh meshing skill with comprehensive documentation gathered from online sources, local tutorials, and existing codebase patterns
version: 1.0.0
module: gmsh-meshing
session:
  id: 2026-02-15-gmsh-skill
  agent: claude
review: pending
---

# WRK-139: Develop gmsh Skill and Documentation

## Context

gmsh 4.15.0 is installed at `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe` with 21 tutorials (.geo + Python), examples (api, boolean, post_processing, simple_geo, struct), and full Python/C/C++ API bindings. The workspace-hub needs a dedicated gmsh skill for consistent mesh generation workflows, particularly for hydrodynamic BEM analysis (AQWA, OrcaWave, Nemoh).

**Existing content audit:**
- `.claude/skills/data/scientific/cad-mesh-generation/SKILL.md` (1074 lines) — covers gmsh basics (panel mesh, volume mesh, quality, GDF/CDB export) but mixed with FreeCAD content
- `.claude/skills/engineering/marine-offshore/mesh-utilities/SKILL.md` (522 lines) — mesh inspection/conversion, minimal gmsh
- `.claude/agent-library/` has `gmsh.json` registered but no detailed skill

**Gaps the new skill fills:**
- gmsh CLI reference (batch commands, options)
- .geo scripting language reference
- Python API comprehensive reference (all key modules)
- OpenCASCADE kernel operations and boolean CSG
- Transfinite/structured meshing
- Field-based mesh density control
- STEP/STL/IGES import workflows
- Box barge and marine geometry meshing patterns
- Integration recipes for AQWA (.DAT), OrcaWave, Nemoh, BEMRosetta
- Reference documentation assets

## Plan

### Step 1: Create skill directory and SKILL.md

**File**: `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md` (new)

Create dedicated gmsh skill with these sections:

```
Frontmatter (name, version, category, description, tags, platforms, invocation)
1. When to Use This Skill
2. Quick Reference (executable path, formats table, algorithms table)
3. CLI Reference (batch meshing, format conversion, key flags)
4. GEO Scripting Language
   - Points, Lines, Surfaces, Volumes
   - Curve Loops, Surface Loops
   - Transformations (Translate, Rotate, Extrude)
   - OpenCASCADE kernel (SetFactory, Box, Sphere, Boolean ops)
   - Physical Groups
5. Python API Reference
   - Initialization and model management
   - gmsh.model.geo (built-in kernel)
   - gmsh.model.occ (OpenCASCADE kernel)
   - gmsh.model.mesh (generation, transfinite, optimization)
   - gmsh.option (algorithm selection, size control)
   - gmsh.model.mesh.field (distance, threshold, background)
   - gmsh.write / gmsh.fltk
6. Mesh Generation Workflows
   - Box barge surface mesh (BEM)
   - Cylinder panel mesh
   - STEP/STL import and remesh
   - Transfinite structured mesh
   - Field-based refinement
7. Solver Integration
   - Export to AQWA (.DAT format)
   - Export to WAMIT (GDF format)
   - Export to Nemoh/BEMRosetta
   - MSH v2.2 for BEM tools
   - Quality targets for hydrodynamic analysis
8. Mesh Quality Assessment
   - Gamma, Eta, Rho metrics
   - Adjacent panel ratio checks
   - BEM-specific quality targets
9. Troubleshooting
10. Resources (online docs, local tutorials index)
```

### Step 2: Create reference documentation asset

**File**: `.claude/skills/engineering/cad/gmsh-meshing/assets/gmsh-reference.md` (new)

Condensed reference doc containing:
- Complete CLI options table (from `gmsh -help` output)
- All mesh algorithm IDs and descriptions
- All supported file formats (input/output)
- Key `gmsh.option` settings with defaults
- Tutorial index (t1-t21 with one-line descriptions)
- Links to online resources

### Step 3: Update work item with plan and cross-references

**File**: `.claude/work-queue/working/WRK-139.md` (edit)

- Add `## Plan` section with this plan content
- Set `plan_approved: true` after user approval
- Add cross-references to existing skills

### Step 4: Regenerate INDEX.md

**Command**: `python .claude/work-queue/scripts/generate-index.py`

## Key Design Decisions

1. **Separate skill, not extension** — gmsh deserves its own skill because it's a standalone tool with CLI, scripting language, and Python API. The existing `cad-mesh-generation` mixes FreeCAD + gmsh; a dedicated skill is cleaner for on-demand loading.

2. **Location**: `.claude/skills/engineering/cad/gmsh-meshing/` — alongside `cad-engineering/` and `freecad-automation/` in the CAD category.

3. **Cross-reference, don't duplicate** — Link to `cad-mesh-generation` for GDF/CDB conversion code and `mesh-utilities` for post-generation inspection. Don't copy those implementations.

4. **Marine/BEM focus** — Since this workspace's primary use case is hydrodynamic analysis, emphasize surface meshing for BEM solvers over volume meshing for FEA.

5. **Executable path** — Reference `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe` for CLI examples; note cross-platform path handling.

## Files Modified

| File | Action | Description |
|------|--------|-------------|
| `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md` | Create | Main skill file (~600-800 lines) |
| `.claude/skills/engineering/cad/gmsh-meshing/assets/gmsh-reference.md` | Create | Condensed reference doc |
| `.claude/work-queue/working/WRK-139.md` | Edit | Add plan section, update frontmatter |
| `.claude/work-queue/INDEX.md` | Regenerate | Reflect updated status |

## Verification

1. Skill file renders correctly in markdown
2. All code examples are syntactically valid (Python + .geo)
3. CLI commands reference correct flags per gmsh 4.15.0
4. Cross-references to existing skills are accurate
5. Executable path is correct and accessible
6. Tutorial index matches local installation content
