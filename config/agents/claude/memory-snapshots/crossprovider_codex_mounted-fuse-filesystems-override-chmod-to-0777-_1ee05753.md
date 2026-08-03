---
name: crossprovider codex mounted-fuse-filesystems-override-chmod-to-0777-
description: Mounted FUSE filesystems override chmod to 0777; owner-only validation must use local tmpfs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [filesystem-quirks, privacy-boundaries, security-testing]
---

FUSE mounts (NFS, SMB) on /mnt coerce file mode to world-readable, failing owner-only security checks. Owner-only sensitive-data validation must write test fixtures to actual /tmp or other local chmod-capable filesystem, not mounted worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
