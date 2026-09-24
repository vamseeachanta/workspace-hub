---
name: crossprovider codex default-verdict-is-non-approve-for-adversarial-r
description: Default verdict is non-approve for adversarial reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-stance, plan-review]
---

Return APPROVE only when you have affirmatively verified each correctness-critical claim and found no gaps. When in doubt, return MINOR or MAJOR. Being wrong about MINOR is cheap; missing a MAJOR is expensive. An empty review without findings is a failure, not an implicit APPROVE.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
