---
name: crossprovider codex fixture-design-synthetic-complete-data-masks-rea
description: Fixture design: synthetic complete data masks real-world partial merges
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [test-design, fixtures]
---

Test fixtures with all fields/products present hide real-world merge defects (oil-only rows with missing gas, vice versa). Add sparse fixtures with intentional `NA`/missing counterparts to catch serialization and coercion bugs before they surface in generated artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
