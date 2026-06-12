---
name: crossprovider hermes force-push-with-lease-after-rebase-violates-no-f
description: Force-push-with-lease after rebase violates no-force-push safety preference
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-safety, no-force-push, branch-cleanup]
---

Using `git push --force-with-lease` after rebasing a branch breaks the stricter no-force-push rule, even if the branch is "already contained". Instead: verify unique commits vs origin/main are zero, then cleanly delete remote branch without rewriting history.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
