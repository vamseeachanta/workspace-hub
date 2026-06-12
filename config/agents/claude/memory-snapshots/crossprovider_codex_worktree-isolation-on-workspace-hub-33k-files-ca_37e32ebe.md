---
name: crossprovider codex worktree-isolation-on-workspace-hub-33k-files-ca
description: Worktree isolation on workspace-hub: 33K files cause 17min–1h+ variance
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [worktree, performance, infrastructure]
---

Using `isolation: worktree` triggers wide checkout variance (17min one run, 1h+ stalled under parallel I/O). Sanity-poll at 5min; if dir absent, kill and pivot. Reserve worktrees for commit/push agents only; avoid for research/exploration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
