---
name: crossprovider codex broad-git-status-commands-may-timeout-on-fuse-mo
description: Broad git status commands may timeout on FUSE-mounted directories
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [git, performance, filesystem, workspace-hub]
---

In workspace-hub and similar FUSE-mounted repositories, `git status` can hang for a minute+ due to filesystem latency. Use targeted alternatives: `git ls-files`, `git diff --name-only`, and `git rev-parse` for specific checks instead of scanning the full working tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
