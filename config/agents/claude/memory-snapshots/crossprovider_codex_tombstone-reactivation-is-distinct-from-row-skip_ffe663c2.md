---
name: crossprovider codex tombstone-reactivation-is-distinct-from-row-skip
description: Tombstone reactivation is distinct from row skip
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tombstones, state-machines, incremental-indexing]
---

Row reactivation on file reappearance (after deletion) requires explicit logic: skip if size/mtime unchanged AND status=='active', but reactivate if the file reappears later. This is not the same as skipping unchanged rows; test it as a separate case with tombstone+reappear scenarios.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
