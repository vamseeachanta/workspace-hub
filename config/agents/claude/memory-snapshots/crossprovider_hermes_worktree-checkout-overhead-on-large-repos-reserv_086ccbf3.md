---
name: crossprovider hermes worktree-checkout-overhead-on-large-repos-reserv
description: Worktree checkout overhead on large repos; reserve for critical agents
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree, large-repo, performance, timeout]
---

Full worktree setup on 30K+ file repos triggers expensive checkout (17min–1h+) and can exceed 60% timeout budget on workspace-hub. Reserve worktree isolation for commit/push-critical agents; use alternative branches for non-mutating work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
