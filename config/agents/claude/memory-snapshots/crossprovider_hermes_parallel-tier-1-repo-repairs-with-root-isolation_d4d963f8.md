---
name: crossprovider hermes parallel-tier-1-repo-repairs-with-root-isolation
description: Parallel tier-1 repo repairs with root isolation and sequence gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, repo-isolation, git-lock-avoidance]
---

Execute CI/test repairs across 6+ tier-1 repos in parallel via subagents; enforce root/nested repo isolation (root must not edit nested, tier-1 must not edit siblings/root). Use task-list preservation across context compression for coordination; serialize commits or use worktrees to avoid git lock races.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
