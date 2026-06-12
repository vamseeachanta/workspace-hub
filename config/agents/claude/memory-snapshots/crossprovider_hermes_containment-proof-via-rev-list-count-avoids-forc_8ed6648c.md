---
name: crossprovider hermes containment-proof-via-rev-list-count-avoids-forc
description: Containment proof via rev-list count avoids force-push; safe for branch cleanup
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, branch-cleanup, force-push-avoidance]
---

Use `git rev-list --count origin/main..BRANCH == 0` to prove a branch's commits are already in origin/main before deletion. This containment proof is safe evidence for cleanup without force-push. If the count is zero, the branch is safe to delete without rebase/force.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
