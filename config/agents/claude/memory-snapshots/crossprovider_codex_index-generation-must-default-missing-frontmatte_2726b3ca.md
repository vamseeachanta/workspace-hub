---
name: crossprovider codex index-generation-must-default-missing-frontmatte
description: Index generation must default missing frontmatter fields across all item statuses
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [automation-debt, index-generation, schema-evolution]
---

When adding new fields (e.g. `computer:`) to WRK item templates, index generation scripts that read archived items will crash on missing fields unless defaults are applied. Field availability varies by item age/status; normalize at render time, not at backfill time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
