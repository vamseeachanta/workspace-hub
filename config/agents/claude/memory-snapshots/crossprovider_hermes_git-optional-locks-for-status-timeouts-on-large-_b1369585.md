---
name: crossprovider hermes git-optional-locks-for-status-timeouts-on-large-
description: GIT_OPTIONAL_LOCKS for status timeouts on large repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, large-repo, performance]
---

git status can timeout on workspace-hub (33K+ files) under heavy I/O; use GIT_OPTIONAL_LOCKS=0 git status and scope to specific paths (--short, git status -- <path>) to avoid zombie git processes accumulating in long sessions. Stale .git/index.lock blocks commits; detect via pgrep, remove (guarded), then retry.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
