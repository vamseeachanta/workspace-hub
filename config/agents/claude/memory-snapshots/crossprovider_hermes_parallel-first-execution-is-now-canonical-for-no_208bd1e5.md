---
name: crossprovider hermes parallel-first-execution-is-now-canonical-for-no
description: Parallel-first execution is now canonical for non-trivial work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [execution-model, parallel-dispatch, orchestration]
---

Hermes standardized that all work must be pre-classified as single-lane, parallel-readonly, or parallel-worktree before execution starts. This is now enforced across AGENTS.md, AI_ECOSYSTEM_DESIGN.md, and skill definitions (gh-work-execution, issue-planning-mode). Classification determines dispatch strategy.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
