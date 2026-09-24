---
name: crossprovider codex codex-sandboxes-cannot-write-to-worktrees
description: Codex sandboxes cannot write to worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, sandbox, environment, worktree, task-routing]
---

OpenAI/Codex agents can write only to the primary workspace, not to sibling worktrees; attempts fail with 'Read-only file system'. This affects task routing—implementation work in worktrees must run on Claude or other agents with filesystem write access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
