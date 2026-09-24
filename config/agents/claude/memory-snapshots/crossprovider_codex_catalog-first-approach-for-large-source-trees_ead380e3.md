---
name: crossprovider codex catalog-first-approach-for-large-source-trees
description: Catalog-first approach for large source trees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, workflow, architecture]
---

Use index/catalog files and database queries before filesystem walks. This respects read-only/sandbox constraints, is more efficient, and provides authoritative counts. Validate catalogs against live filesystem post-extraction; pre-extraction walks are wasteful on massive trees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
