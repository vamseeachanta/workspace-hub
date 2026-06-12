---
name: crossprovider hermes approval-gate-must-bind-exact-plan-sha
description: Approval-gate must bind exact plan SHA
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gate, plan-review, git, binding]
---

Approval marker must cite the reviewed plan's exact git/blob SHA. Implementation must preflight that current plan SHA matches approved SHA before edits begin. Prevent approval-marker drift by making SHA binding non-optional in gate definition.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
