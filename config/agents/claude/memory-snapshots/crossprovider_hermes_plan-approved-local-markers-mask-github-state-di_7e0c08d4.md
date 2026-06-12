---
name: crossprovider hermes plan-approved-local-markers-mask-github-state-di
description: Plan-approved local markers mask GitHub state divergence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-gates, plan-approval, hermes-workflow]
---

Stale `.planning/plan-approved/` files can exist locally without corresponding `status:plan-approved` label on GitHub. Hermes #2747 attempted implementation blocked on live label, but local marker created false positive impression of approval. Remove local markers before checking live issue state to avoid gate-bypass.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
