---
name: crossprovider hermes approval-gates-require-explicit-resolution-befor
description: Approval gates require explicit resolution before autonomous implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, governance, autonomous-work, safety-check]
---

Issues blocked by missing `.planning/plan-approved/` files or unresolved re-review states cannot be safely implemented autonomously. Codex bundles correctly skip security-setting and scheduled-task changes when approval status is unclear; these remain `blocked_partial` and require user/governance input.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
