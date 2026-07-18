---
name: crossprovider codex keyset-pagination-fixes-sqlite-row-visit-bounds-
description: Keyset pagination fixes SQLite row-visit bounds better than OFFSET
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [sqlite, pagination, testing]
---

When a fill query uses `OFFSET` to skip a seed row, SQLite still evaluates the seed row's predicate, causing N+1 row visits for N results. Replace with `WHERE primary_key > seed_value` and deterministic ordering. However, text primary keys may still examine more internal candidates than integer keys; test both types separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
