---
name: crossprovider gemini schema-validation-enforcement-progression-warn-m
description: Schema validation enforcement progression: warn-mode then blocking-mode
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [enforcement, ci, schema, governance]
---

Gate required frontmatter on active WRK items via CI checks. Start in warn-mode to surface violations without blocking. Migrate to blocking-mode once compliance reaches acceptable threshold. Prevents surprise breakage.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
