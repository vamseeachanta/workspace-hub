---
name: crossprovider hermes branch-must-be-synced-to-origin-main-before-merg
description: Branch must be synced to origin/main before merge; behind-N is a blocker
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [branch-hygiene, merge-readiness, git-workflow]
---

Before final commit/push/merge, branch must be up-to-date with `origin/main`. A branch that is "behind N" commits introduces stale integration and merge conflicts. Rebase or merge origin/main first; never commit while behind.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
