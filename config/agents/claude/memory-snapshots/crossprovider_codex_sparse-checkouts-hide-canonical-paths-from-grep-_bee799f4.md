---
name: crossprovider codex sparse-checkouts-hide-canonical-paths-from-grep-
description: Sparse checkouts hide canonical paths from grep/ls
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [git, sparse-checkout, verification]
---

A path named in a plan may exist at HEAD but be sparse-excluded from your checkout. Use `git ls-tree`, `git show HEAD:path`, or `git grep` on the remote to verify existence. Implementation must account for widening sparse scope when modifying excluded paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
