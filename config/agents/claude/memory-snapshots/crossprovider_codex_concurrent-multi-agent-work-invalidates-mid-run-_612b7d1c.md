---
name: crossprovider codex concurrent-multi-agent-work-invalidates-mid-run-
description: Concurrent multi-agent work invalidates mid-run assumptions about branches/worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-agent-safety, concurrent-work, branch-persistence]
---

In multi-agent sessions, external processes can merge feature branches, remove worktrees, and advance upstream refs during an active session. Worktree persistence and branch availability should be re-verified before beginning destructive operations, not assumed to remain stable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
