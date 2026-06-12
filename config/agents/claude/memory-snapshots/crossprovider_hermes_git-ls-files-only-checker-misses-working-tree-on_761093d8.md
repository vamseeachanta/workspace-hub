---
name: crossprovider hermes git-ls-files-only-checker-misses-working-tree-on
description: Git ls-files-only checker misses working-tree-only drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-structure, git-mechanics, scope-clarity]
---

A checker using only `git ls-files` catches tracked and staged content violations but cannot detect untracked files in ignored directories or untracked files in allowed roots. Document this scope limitation explicitly if it differs from the plan promise.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
