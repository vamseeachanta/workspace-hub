---
name: crossprovider codex ntfs-workspace-broad-scans-cause-disk-saturation
description: NTFS workspace broad scans cause disk saturation and git hangs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [workspace-constraint, i-o-discipline, ntfs-fuse, diagnostics]
---

Parallel recursive scans (find, rg, git status) on `/mnt/local-analysis` saturate disk I/O and cause operations like `git status` to hang. Require bounded scans with pruning, timeouts, and I/O-pressure preflight checks before spawning parallel audits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
