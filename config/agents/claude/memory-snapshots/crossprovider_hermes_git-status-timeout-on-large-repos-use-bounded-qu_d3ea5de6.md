---
name: crossprovider hermes git-status-timeout-on-large-repos-use-bounded-qu
description: git status timeout on large repos; use bounded queries instead
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, large-repo, workspace-hub, performance]
---

`bash scripts/repository_sync status work` times out on workspace-hub scale (~19K files). Use targeted queries: `git diff --name-only`, `git ls-files --others --exclude-standard | head`, or `git status --untracked-files=no` to avoid lock contention.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
