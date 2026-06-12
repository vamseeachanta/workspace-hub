---
name: crossprovider hermes preserve-unrelated-dirty-workspace-state-during-
description: Preserve unrelated dirty workspace state during issue work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-management, issue-scope, parallel-work]
---

During implementation of a specific GitHub issue: do not clean, stage, or commit unrelated modified/untracked files. Only commit changes scoped to the issue; preserve other work in place for parallel agent sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
