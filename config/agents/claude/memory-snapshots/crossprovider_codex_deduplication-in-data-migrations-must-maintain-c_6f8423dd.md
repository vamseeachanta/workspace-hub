---
name: crossprovider codex deduplication-in-data-migrations-must-maintain-c
description: Deduplication in data migrations must maintain consistency across all duplicate instances
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [data-migration, consistency, deduplication]
---

Backfill operations that normalize rows independently break the invariant that all instances of a duplicate key have the same state/provenance. Apply the migration atomically to all duplicates or track duplicate groups explicitly and migrate together.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
