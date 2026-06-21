---
name: crossprovider codex codex-parallel-read-only-audits-coordinate-to-av
description: Codex parallel read-only audits: coordinate to avoid duplicate broad traversals
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [coordination, performance, shared-resources, process-management]
---

When multiple Codex processes run similar searches (e.g., full-tree grep over large shared mounts), check active processes first and bias toward targeted repo-scoped probes instead of full-tree scans. Parallel broad searches waste I/O and create stale/reparented processes stuck in uninterruptible I/O. Only kill processes you started.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
