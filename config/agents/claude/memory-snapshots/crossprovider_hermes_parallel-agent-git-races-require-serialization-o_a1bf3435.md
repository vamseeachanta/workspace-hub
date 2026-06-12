---
name: crossprovider hermes parallel-agent-git-races-require-serialization-o
description: Parallel agent git races require serialization or worktrees
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, parallel, concurrency]
---

4 parallel agents writing to main hit git lock contention. Either serialize commits (commits target unique files) or use isolated worktrees+branches. Sessions that mix parallel writes without boundaries lose commits silently.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
