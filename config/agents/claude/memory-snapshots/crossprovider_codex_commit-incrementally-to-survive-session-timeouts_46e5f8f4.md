---
name: crossprovider codex commit-incrementally-to-survive-session-timeouts
description: Commit incrementally to survive session timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, session-management, risk-mitigation]
---

A 55-minute session was killed mid-work before committing anything; work survived only because it persisted in the worktree. Commit each verified increment as it completes rather than batching one final commit at the end. Small commits on feature branches are preferred and safe.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
