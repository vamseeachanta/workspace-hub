---
name: crossprovider codex computing-size-metadata-on-quarantined-data-requ
description: Computing size metadata on quarantined data requires early short-circuit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [quarantine, traversal, metadata, private-data]
---

Operations like `du` or stat-based size checks can require traversing into private directory entries before the quarantine gate prevents it. Private/unknown roots must short-circuit before size operations, using only precomputed caches or skipping entirely with a test assertion that the size function is never called on private paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
