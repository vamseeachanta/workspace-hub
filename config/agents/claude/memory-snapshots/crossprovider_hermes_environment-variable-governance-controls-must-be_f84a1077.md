---
name: crossprovider hermes environment-variable-governance-controls-must-be
description: Environment-variable governance controls must be actively enforced in hooks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, enforcement, hooks, bug-pattern]
---

Scripts that export governance flags (FORCE_PLAN_GATE_STRICT, DISABLE_ENFORCEMENT) are ineffective if consuming hooks don't explicitly read them; silence = no enforcement. The plan-approval-gate hook neither reads nor acts on these exports, rendering them inert. Governance controls are executable code, not documentation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
