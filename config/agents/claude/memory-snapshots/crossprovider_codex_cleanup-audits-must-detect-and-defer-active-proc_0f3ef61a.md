---
name: crossprovider codex cleanup-audits-must-detect-and-defer-active-proc
description: Cleanup audits must detect and defer active process artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [cleanup, tmp, parallel-work, audit]
---

Before removing /tmp artifacts, enumerate git worktree list and check modification times to detect in-flight work. Multiple concurrent sessions may be writing to the same /tmp cleanup directory; deferring removal of recent artifacts and worktree-related paths avoids interrupting active processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
