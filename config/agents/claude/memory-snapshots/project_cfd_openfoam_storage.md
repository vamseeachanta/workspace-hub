---
name: CFD/OpenFOAM storage strategy
description: OpenFOAM input files in digitalmodel repo, large output volumes stored on disk outside git, handled with appropriate data management
type: project
---

CFD/OpenFOAM work storage strategy:
- **Input files** (case setup, mesh definitions, boundary conditions): managed in digitalmodel repo
- **Output files** (results, VTK, postProcessing): stored on disk OUTSIDE git — volumes too large for version control
- Output location: `/mnt/ace/` or `/mnt/dde/` data drives (shared across machines)

**Why:** OpenFOAM outputs (field data, VTK meshes, time directories) can be GB-scale per case. These must stay on disk with appropriate indexing, not in git.

**How to apply:** When setting up OpenFOAM workflows, ensure case directories separate input (git-tracked in digitalmodel) from output (disk-stored, indexed in doc index). Use symlinks or config to point runs at the output location.
