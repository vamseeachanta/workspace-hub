---
name: crossprovider hermes parallel-execution-git-lock-avoidance-via-worktr
description: Parallel execution: git-lock avoidance via worktree + commit serialization
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, git-lock, serialization]
---

Parallel agents racing on git lock cause silent-revert, retry-loop reset hazard. Pattern: agents write files only; main session serializes commits. For shared-target work, partition into unique-target (subagent writes) + manifest delta (main applies). Use `SKIP_PUSH=1 git commit` to prevent post-commit hook defeating test gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
