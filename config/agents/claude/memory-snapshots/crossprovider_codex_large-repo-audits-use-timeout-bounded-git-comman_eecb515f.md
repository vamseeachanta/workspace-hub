---
name: crossprovider codex large-repo-audits-use-timeout-bounded-git-comman
description: Large-repo audits: use timeout-bounded Git commands to avoid untracked-file hangs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit-methodology, git-performance, large-repos]
---

When auditing Git repositories for dirty counts or metadata, `git status` can hang traversing untracked files in large trees. Use `git status -uno` and timeout-bound probes (1s per repo); report timeouts explicitly rather than attempting full-tree walks that can dominate audit execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
