---
name: crossprovider codex incremental-backups-with-link-dest-need-explicit
description: Incremental backups with --link-dest need explicit snapshot layout, not just the flag
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [backup-strategy, incremental-sync, scheduling]
---

`--link-dest` alone does not define snapshot semantics. Safe incremental backup requires timestamped snapshot directories (e.g., `.../snapshots/YYYY-MM-DD_HHMMSS/`), a `latest` symlink for reference, retention policy, atomic completion (write to temp, rename on success), and locking to prevent overlaps on scheduled runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
