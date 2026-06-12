---
name: crossprovider hermes worktree-materialization-variance-is-load-profil
description: Worktree materialization variance is load-profile dependent, not static
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-performance, parallel-agents, io-bottleneck, worktree]
---

Large worktrees (19K files) show 10x timing variance (17min to 1h+) based on concurrent I/O under parallel-agent load. Sanity-poll at 5min; if directory absent after timeout, kill process + pivot to fallback. Do not assume static performance benchmarks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
