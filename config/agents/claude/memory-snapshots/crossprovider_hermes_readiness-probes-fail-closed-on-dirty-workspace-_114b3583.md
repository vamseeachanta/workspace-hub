---
name: crossprovider hermes readiness-probes-fail-closed-on-dirty-workspace-
description: Readiness probes fail-closed on dirty workspace state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness-gates, git-state-management, dispatch-workflow]
---

Dispatch readiness scripts are designed to fail-closed when the working copy has uncommitted/untracked changes. Dirty state must be explicitly classified (expected vs. unexpected), preserved, and committed before readiness passes. This prevents dispatch with incomplete state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
