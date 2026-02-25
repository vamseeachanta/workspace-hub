---
id: WRK-139
title: Develop gmsh skill and documentation
status: archived
archived_at: 2026-02-16T15:45:00Z
priority: medium
complexity: medium
compound: false
created_at: 2026-02-15T00:00:00Z
target_repos:
  - workspace-hub
commit:
spec_ref:
related: []
blocked_by: []
synced_to: []
plan_reviewed: true
plan_approved: true
percent_complete: 100
brochure_status:
---

# Develop gmsh Skill and Documentation

## What
Create a gmsh skill for the workspace-hub ecosystem that documents how to use the gmsh meshing program, including API usage, CLI commands, and integration patterns. Gather all required documentation, user manuals, and reference material from online sources and the local installation.

## Why
gmsh is a powerful open-source 3D finite element mesh generator with built-in CAD engine and post-processor. Having a dedicated skill enables consistent mesh generation workflows for hydrodynamic and structural analysis across the workspace-hub projects (e.g., digitalmodel diffraction analysis).

## Context
- **gmsh executable**: `D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe`
- **Local tutorials**: `D:\software\gmsh\gmsh-4.15.0-Windows64\tutorials/` (t1-t21 .geo files + Python/C++/C/Julia/Fortran examples)
- **Local examples**: `D:\software\gmsh\gmsh-4.15.0-Windows64\examples/` (api/, boolean/, post_processing/, simple_geo/, struct/)
- **Version**: gmsh 4.15.0

## Acceptance Criteria
- [x] Research gmsh online documentation, API reference, and user manual
- [x] Review local tutorials (t1-t21) and Python API examples
- [x] Create gmsh skill file at `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md`
- [x] Document key gmsh CLI commands and options
- [x] Document Python API usage patterns (gmsh.initialize, gmsh.model, gmsh.mesh)
- [x] Document common mesh generation workflows (box barge, cylinder, import STEP/STL)
- [x] Include integration patterns with existing solvers (AQWA, OrcaWave/Nemoh)
- [x] Store key reference docs/summaries in skill assets folder

## Plan

### Deliverables

| File | Action | Description |
|------|--------|-------------|
| `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md` | Created | Main skill (~700 lines): CLI, .geo scripting, Python API, OCC kernel, workflows, solver integration |
| `.claude/skills/engineering/cad/gmsh-meshing/assets/gmsh-reference.md` | Created | Condensed reference: all CLI options, algorithms, formats, options, tutorial index |
| `.claude/work-queue/working/WRK-139.md` | Updated | Plan section, acceptance criteria marked complete |

### Design Decisions

1. **Separate skill** — gmsh has its own CLI, scripting language, and Python API; warrants dedicated skill vs extending `cad-mesh-generation`
2. **Location**: `.claude/skills/engineering/cad/gmsh-meshing/` — alongside `cad-engineering/` and `freecad-automation/`
3. **Cross-reference, don't duplicate** — Links to `cad-mesh-generation` for GDF/CDB export and `mesh-utilities` for inspection
4. **Marine/BEM focus** — Emphasizes surface meshing for hydrodynamic BEM solvers over volume meshing for FEA

### Cross-References

- `skills/data/scientific/cad-mesh-generation/SKILL.md` — FreeCAD + gmsh workflows, GDF/CDB export code
- `skills/engineering/marine-offshore/mesh-utilities/SKILL.md` — mesh inspection, conversion, quality checks
- `skills/engineering/cad/cad-engineering/SKILL.md` — general CAD engineering
- `skills/engineering/cad/freecad-automation/SKILL.md` — FreeCAD automation (depends on gmsh-meshing)

---
*Source: develop gmsh skill and documentation; gmsh program at "D:\software\gmsh\gmsh-4.15.0-Windows64\gmsh.exe", get all required documentation, user manuals, etc. ready by researching online and examples and tutorials in folder D:\software\gmsh*
