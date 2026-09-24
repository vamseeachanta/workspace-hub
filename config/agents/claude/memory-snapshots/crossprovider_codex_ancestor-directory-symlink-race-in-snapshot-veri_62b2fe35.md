---
name: crossprovider codex ancestor-directory-symlink-race-in-snapshot-veri
description: Ancestor-directory symlink race in snapshot verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [symlink, race-condition, sqlite, filesystem]
---

SQLite connections can read alternate files through briefly-substituted symlinked parent directories before post-open validation runs. File identity checks (inode, digest, sidecar) passed while the connection accessed an unintended alternate file.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
