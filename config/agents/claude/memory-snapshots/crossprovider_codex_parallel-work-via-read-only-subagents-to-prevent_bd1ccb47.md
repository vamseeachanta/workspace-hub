---
name: crossprovider codex parallel-work-via-read-only-subagents-to-prevent
description: Parallel work via read-only subagents to prevent shared-target races
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, git-operations, subagent-pattern]
---

When repository mandates parallel dispatch for independent audits, dispatch read-only subagents for finding clusters while sequencing all edits and TDD in the main worktree. This pattern avoids git-lock contention and ensures coherent commit lineage even with concurrent review passes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
