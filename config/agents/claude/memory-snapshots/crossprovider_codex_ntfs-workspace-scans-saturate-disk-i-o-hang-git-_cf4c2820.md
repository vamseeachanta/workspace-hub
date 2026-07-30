---
name: crossprovider codex ntfs-workspace-scans-saturate-disk-i-o-hang-git-
description: NTFS workspace scans saturate disk I/O, hang git operations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-23
  tags: [I/O-discipline, NTFS-FUSE, workspace-health, scan-patterns]
---

Broad `find`/`rg` scans against `/mnt/local-analysis` (NTFS-FUSE mount) saturate the workspace disk and stall `git status`. Parallel audits need I/O-pressure preflights, bounded scans with pruning/timeouts, and cleanup of interrupted scanner processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
