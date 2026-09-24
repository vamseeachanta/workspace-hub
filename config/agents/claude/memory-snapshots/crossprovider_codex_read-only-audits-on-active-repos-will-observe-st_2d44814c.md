---
name: crossprovider codex read-only-audits-on-active-repos-will-observe-st
description: Read-only audits on active repos will observe state drift; snapshot timing and note concurrency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audits, concurrency, state-drift, timing]
---

Concurrent operations (push, stage, worktree creation) change repo state during read-only audits, causing worktree counts and ref states to shift mid-audit. Record audit timestamp and note concurrent processes so later actions don't misinterpret transient drift as permanent state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
