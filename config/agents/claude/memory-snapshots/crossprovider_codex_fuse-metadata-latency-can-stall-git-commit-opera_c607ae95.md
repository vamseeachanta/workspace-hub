---
name: crossprovider codex fuse-metadata-latency-can-stall-git-commit-opera
description: FUSE metadata latency can stall git commit operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, debugging, git]
---

On FUSE-backed repositories, git commits can block indefinitely during hook/metadata phases. Disabling `preloadIndex` or status traversal does not eliminate the underlying FUSE request; affects recovery/automation when machines are remote or under load.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
