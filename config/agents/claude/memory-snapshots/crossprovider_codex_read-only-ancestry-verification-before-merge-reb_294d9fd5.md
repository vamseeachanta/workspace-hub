---
name: crossprovider codex read-only-ancestry-verification-before-merge-reb
description: Read-only ancestry verification before merge/rebase decisions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [git, ancestry, branch-management, published-branches]
---

Before deciding whether to merge or rebase a published feature branch, verify ancestor lineage in read-only mode: merge-base, first-parent ancestry, and exact commits behind main. Being N commits behind main is not the same as stale if the branch was created after a critical merge; verify that merge is an ancestor of the feature HEAD. This prevents unnecessary rebases on published branches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
