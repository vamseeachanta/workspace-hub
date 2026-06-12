---
name: crossprovider codex category-enumerations-must-cover-all-values-used
description: Category enumerations must cover all values used by production taxonomy tools
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [taxonomy-design, completeness, coverage]
---

Incomplete category maps (e.g., missing `uncategorised` from a map used by infer-category.py and generate-index.py) leave agents without guidance for real WRK values. Audit all category-producing tools to find the complete set, then update all downstream maps atomically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
