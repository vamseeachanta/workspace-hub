---
name: crossprovider hermes detect-active-parallel-work-via-process-command-
description: detect active parallel work via process command line and worktree list
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-work, concurrency-safety, process-detection]
---

Overnight batch workers advertise claimed scope (worktree path, branch, issue#, owned files) in their `claude -p` process command line. Use `ps -ef | grep 'claude -p'` to find active workers, then verify with `git worktree list`. Main session should skip claimed paths to prevent git lock races and commit conflicts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
