---
name: resource-intelligence-categorymining-map
description: "Sub-skill of resource-intelligence: Category\u2192Mining Map."
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Category→Mining Map

## Category→Mining Map


Read `category` and `subcategory` from WRK frontmatter. Use this table to select which mining categories to prioritise.

| WRK `category` | High-priority mining | Low-priority (skip unless relevant) |
|----------------|---------------------|--------------------------------------|
| `harness` | 1 Skills, 2 Prior WRKs, 3 Memory, 6 Workspace docs | 7 Document index, 8 Mounted sources |
| `engineering` | 4 Existing code, 7 Document index, 8 Mounted sources | 9 Online (check index first) |
| `data` | 4 Existing code, 5 Specs, 7 Document index | 8 Mounted sources |
| `platform` | 1 Skills, 4 Existing code, 6 Workspace docs | 7 Document index |
| `business` | 3 Memory, 5 Specs, 6 Workspace docs | 7 Document index, 8 Mounted sources |
| `maintenance` | 2 Prior WRKs, 4 Existing code, 6 Workspace docs | 8 Mounted sources, 9 Online |
| `personal` | 3 Memory | all others |
| `uncategorised` | 1 Skills, 2 Prior WRKs, 3 Memory | decide per subcategory |

For any `subcategory` containing `pipeline`, `viv`, `dnv`, `api rp`, `iso`, `fea`, `cfd`, `ansys`, `orcaflex` → always include categories 7 and 8 regardless of `category`.

---
