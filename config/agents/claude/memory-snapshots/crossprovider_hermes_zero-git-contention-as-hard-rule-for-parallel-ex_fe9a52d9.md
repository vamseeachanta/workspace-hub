---
name: crossprovider hermes zero-git-contention-as-hard-rule-for-parallel-ex
description: Zero git contention as hard rule for parallel execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git-safety, multi-agent, contention]
---

For parallel multi-agent execution, non-overlapping file/branch/worktree ownership is non-negotiable. This must be explicitly stated in every handoff contract (not assumed), verified in the orchestrator pre-check, and confirmed in the execution start comment. If clear ownership boundaries cannot be stated, do not delegate.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
