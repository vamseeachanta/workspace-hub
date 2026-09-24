---
name: crossprovider codex use-isolated-clones-for-multi-repo-branch-isolat
description: Use isolated clones for multi-repo branch isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, multi-repo]
---

When implementing across multiple repos, create isolated branch checkouts via `git clone` into nested directories rather than reusing shared workspace checkouts. Prevents mixing unrelated work and maintains clean lane scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
