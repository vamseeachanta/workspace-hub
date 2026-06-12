---
name: crossprovider hermes cross-machine-result-sync-via-rsync-update
description: Cross-machine result sync via rsync --update
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-machine, rsync, synchronization]
---

For parallel agent work across machines, pull remote results back with `rsync --update` (only transfers if remote is newer). For scoped syncs, use glob patterns like `rsync ... *ace2*.md` to avoid pulling unrelated files. Verify remote is reachable before attempting pull.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
