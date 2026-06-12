---
name: crossprovider hermes multi-agent-git-contention-on-workspace-hub-requ
description: Multi-agent git contention on workspace-hub requires write-only or worktree isolation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-lock, parallel-agents, workspace-hub]
---

workspace-hub's large size + parallel fleet activity causes git lock races. Pattern: either serialize commits (one agent at a time) OR use worktrees (each agent isolated). For subagent write-only pattern: main session serializes commits of subagent-written files. Parallel `git add && git commit && ...` chains under heavy load hang on first lock contention.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
