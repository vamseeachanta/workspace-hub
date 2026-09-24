---
name: crossprovider codex consumer-surface-mapping-before-fixture-migratio
description: Consumer surface mapping before fixture migration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-governance, refactoring, testing]
---

Before moving or reclassifying shared data fixtures (JSON, test fixtures, generated artifacts), map all active references via grep/search: imports in code, test assertions, index/README mentions, and generated consumers. This prevents orphaning references or leaving misleading metadata in place.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
