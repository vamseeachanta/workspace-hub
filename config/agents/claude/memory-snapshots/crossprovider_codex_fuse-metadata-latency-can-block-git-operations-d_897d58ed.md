---
name: crossprovider codex fuse-metadata-latency-can-block-git-operations-d
description: FUSE metadata latency can block git operations despite index tuning
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [git, filesystem, performance, debugging]
---

On FUSE-backed filesystems (e.g., union mounts, rclone), git commits can stall in metadata collection even when preloadIndex is disabled. The underlying issue is FUSE request latency, not parallel index load; disabling preload reduces amplification but doesn't eliminate blocking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
