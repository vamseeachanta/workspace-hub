---
name: crossprovider hermes plan-reviews-frequently-expose-stale-contradicto
description: Plan reviews frequently expose stale/contradictory claims about artifact existence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, review-process, adversarial-review]
---

Adversarial reviews of #2096, #2105, #2229 revealed plans claiming files don't exist when they're already indexed, or plans re-planning work already completed. Check plan assumptions against git-tracked evidence (ls-files, git log, README indices) before accepting problem statements.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
