---
name: crossprovider codex cleanup-guards-need-device-inode-verification-no
description: Cleanup guards need device/inode verification, not just sentinels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, filesystem, security]
---

A sentinel file in `.git/` (e.g., `.git/managed-dispatch`) is insufficient for cleanup authorization. Must verify the target is not a bind-mount, symlink escape, or outside the owned device/inode range. Otherwise, `rm -rf` can delete mounted content outside the intended root.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
