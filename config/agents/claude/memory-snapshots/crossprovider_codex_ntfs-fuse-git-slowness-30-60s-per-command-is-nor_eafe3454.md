---
name: crossprovider codex ntfs-fuse-git-slowness-30-60s-per-command-is-nor
description: NTFS-FUSE git slowness (30-60s per command) is normal here
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [git, ntfs-fuse, infrastructure]
---

Git operations on /mnt/local-analysis NTFS-FUSE mount are routinely slow. Use `GIT_OPTIONAL_LOCKS=0`, set generous timeouts, and be patient. Do not retry or investigate filesystem issues—this is expected infrastructure behavior, not a fault.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
