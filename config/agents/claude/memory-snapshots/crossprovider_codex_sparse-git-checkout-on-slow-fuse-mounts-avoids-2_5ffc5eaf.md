---
name: crossprovider codex sparse-git-checkout-on-slow-fuse-mounts-avoids-2
description: Sparse git checkout on slow FUSE mounts avoids 22k-file materialization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, fuse-mount, performance, worktree]
---

Full worktree checkout of large repos (22,689 files) stalls on FUSE mounts during index refresh/materialization stage, not content transfer. Sparse cone mode (e.g., `git worktree add --sparse <path> <branch>` with sparse-checkout config) materializes only selected paths (~235 files vs 22k), reducing single-file bottleneck. Local /tmp + sparse is viable when /mnt/local-analysis is slow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
