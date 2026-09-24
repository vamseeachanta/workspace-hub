---
name: crossprovider codex mounted-worktrees-coerce-local-files-to-0777-bre
description: Mounted worktrees coerce .local files to 0777, breaking owner-only checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem, permissions, worktree, environment]
---

When the worktree is mounted (e.g., via NFS or Docker volume), system coerces .local file permissions to 0777, preventing owner-only validation. Owner-only runtime fixtures must reside on chmod-capable filesystems, not the mounted checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
