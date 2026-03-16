---
name: infrastructure-layout-naming-solvers-vs-basesolvers
description: 'Sub-skill of infrastructure-layout: Naming: `solvers/` vs `base_solvers/`.'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Naming: `solvers/` vs `base_solvers/`

## Naming: `solvers/` vs `base_solvers/`


Both names are acceptable. Prefer `solvers/` for new repos. Use `base_solvers/` only
if the repo already has it and renaming would break callers.

| Repo | Canonical name | Notes |
|------|---------------|-------|
| digitalmodel (existing) | `base_solvers/` | Historical; do not rename mid-project |
| new repos | `solvers/` | Preferred |

Never use both simultaneously in the same repo.

---
