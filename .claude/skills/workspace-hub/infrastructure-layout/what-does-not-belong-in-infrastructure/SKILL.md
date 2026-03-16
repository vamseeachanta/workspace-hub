---
name: infrastructure-layout-what-does-not-belong-in-infrastructure
description: 'Sub-skill of infrastructure-layout: What Does NOT Belong in `infrastructure/`.'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# What Does NOT Belong in `infrastructure/`

## What Does NOT Belong in `infrastructure/`


| Item | Correct location |
|------|-----------------|
| Flask/Dash apps, blueprints, routes | `src/<pkg>/web/` |
| Plate capacity / buckling domain solver | `src/<pkg>/structural/plate_capacity/` |
| Reservoir analysis scripts | `src/<pkg>/reservoir/` |
| Domain-specific cathodic protection analysis | `src/<pkg>/structural/cp/` or `src/<pkg>/subsea/cp/` |
| Per-domain data loaders (BSEE, EIA, SODIR) | `src/<pkg>/<domain>/` |
| Unit tests | `tests/infrastructure/` |
| Runtime config for a specific domain | `config/<domain>/` at repo root |
| Generated HTML reports | `reports/` (gitignored) |

---
