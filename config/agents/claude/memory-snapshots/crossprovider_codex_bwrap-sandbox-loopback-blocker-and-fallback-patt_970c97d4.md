---
name: crossprovider codex bwrap-sandbox-loopback-blocker-and-fallback-patt
description: Bwrap sandbox loopback blocker and fallback pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [execution, sandbox, fallback, environment]
---

Shell execution in some environments fails before any command runs: `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`. This blocks git operations, worktree creation, file writes, and script execution. Fallback: use GitHub API/connector for evidence collection and read-only inspection; durable writes may require scheduled/remote execution. Environment appears session-specific; not permanent blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
