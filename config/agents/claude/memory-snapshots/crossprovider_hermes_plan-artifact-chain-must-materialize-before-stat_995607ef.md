---
name: crossprovider hermes plan-artifact-chain-must-materialize-before-stat
description: Plan artifact chain must materialize before status:plan-review transition
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review, artifact-governance, workflow]
---

Issue cannot move to `status:plan-review` until canonical plan exists at `docs/plans/...` path, review artifacts exist at `scripts/review/results/...`, and adversarial review summary is populated from those artifacts. This is a governance requirement, not optional.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
