---
name: crossprovider codex parallel-recursive-scans-saturate-ntfs-workspace
description: Parallel recursive scans saturate NTFS workspace I/O
metadata:
  type: reference
  source: codex
  bridged: 2026-07-22
  tags: [ntfs, io-discipline, workspace, parallel]
---

Concurrent find/rg operations and git commands targeting `/mnt/local-analysis` (NTFS mount) can saturate disk and hang processes. Use bounded scans with directory pruning, operation timeouts, and check I/O pressure before launching parallel audits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
