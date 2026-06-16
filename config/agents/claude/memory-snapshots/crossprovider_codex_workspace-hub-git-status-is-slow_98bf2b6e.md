---
name: crossprovider codex workspace-hub-git-status-is-slow
description: workspace-hub: git status is slow
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [workspace-hub, performance, git, environment]
---

`git status --short` on `/mnt/local-analysis/workspace-hub` takes measurably long (session 2 shows it still running after direct probe); probe with explicit wait rather than starting additional status commands in parallel.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
