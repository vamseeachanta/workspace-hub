---
name: crossprovider codex union-conflict-resolution-for-append-only-files-
description: UNION conflict resolution for append-only files: use stage blobs to avoid markers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, merge, conflict-resolution, automation]
---

When merging append-only files (CSVs, logs, verification queues), resolve by keeping one header and all unique rows from both sides (deduplicated). Extract stage-3 (theirs) and stage-2 (ours) blobs via `git show :2` and `:3` to build the union without conflict markers polluting the output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
