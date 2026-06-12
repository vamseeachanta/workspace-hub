---
name: crossprovider hermes git-status-timeouts-on-30k-file-repos
description: Git status timeouts on 30K+ file repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, large-repo, performance, timeout]
---

Unbounded `git status` hangs on workspace-hub due to untracked-file enumeration at scale; use `GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 -uno` or wrap with timeout to avoid blocking.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
