---
name: crossprovider codex pytest-discovery-hangs-on-fuse-use-byte-compared
description: Pytest discovery hangs on FUSE—use byte-compared /tmp harness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pytest, fuse, workaround]
---

When pytest discovery hangs on FUSE worktrees (serial stat overhead), copy tests to `/tmp`, byte-compare them, and run only the local copy. Use focused test paths to skip unrelated directories. Preserves test validity and git coverage while bypassing FUSE bottleneck.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
