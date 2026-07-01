---
name: crossprovider codex timeout-bound-operations-on-slow-filesystems
description: Timeout-bound operations on slow filesystems
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [performance, environment, timeout]
---

Large mounts or slow filesystems cause unbounded operations like `git status` or recursive `find` to hang. Use timeouts and direct paths instead of scans. Replace with pre-built indices when available.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
