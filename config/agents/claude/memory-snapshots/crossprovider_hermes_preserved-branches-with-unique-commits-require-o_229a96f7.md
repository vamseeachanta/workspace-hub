---
name: crossprovider hermes preserved-branches-with-unique-commits-require-o
description: Preserved branches with unique commits require one-by-one PR/merge validation, not bulk merging
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [branch-hygiene, git-workflow, PR-safety]
---

Branches with commits unique to origin/main must be validated individually: create PR, verify mergeable, check required checks pass, merge, then clean up worktree/remote branch. Blind bulk merge or force operations violate safety constraints and hide blockers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
