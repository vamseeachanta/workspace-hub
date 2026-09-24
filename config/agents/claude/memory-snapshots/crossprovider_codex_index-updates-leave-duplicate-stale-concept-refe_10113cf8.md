---
name: crossprovider codex index-updates-leave-duplicate-stale-concept-refe
description: Index updates leave duplicate/stale concept references
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [indexing, data-consistency, wiki-maintenance]
---

When updating an index entry for a concept, old references to the same concept can remain as stale duplicate rows later in the same index. Index edits require comprehensive cleanup: grep for the concept across the full index and consolidate or remove stale rows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
