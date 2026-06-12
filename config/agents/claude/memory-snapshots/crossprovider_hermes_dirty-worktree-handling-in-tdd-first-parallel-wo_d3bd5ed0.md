---
name: crossprovider hermes dirty-worktree-handling-in-tdd-first-parallel-wo
description: Dirty worktree handling in TDD-first parallel work inheritance
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, parallel-work, git-workflow]
---

When inheriting uncommitted/dirty state from a previous worker session, inspect diffs first to understand the state before cleaning or overwriting. Treat dirty files as legitimate work-in-progress, not as noise. This surfaces incomplete patches, test additions, and fixture changes that inform next steps.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
