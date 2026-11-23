---
name: gmsh-openfoam-orcaflex-real-mode-requirements
description: 'Sub-skill of gmsh-openfoam-orcaflex: Real Mode Requirements.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Real Mode Requirements

## Real Mode Requirements


| Solver | Installation | Check |
|--------|-------------|-------|
| Gmsh | `pip install gmsh` | `python3 -c "import gmsh"` |
| OpenFOAM v2312 | ESI apt repo | `source /usr/lib/openfoam/openfoam2312/etc/bashrc` |
| OrcFxAPI | Orcina license | `python3 -c "import OrcFxAPI"` |

The pipeline auto-detects availability and falls back to stubs gracefully.
