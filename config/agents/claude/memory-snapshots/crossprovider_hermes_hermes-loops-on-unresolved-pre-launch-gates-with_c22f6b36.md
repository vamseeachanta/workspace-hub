---
name: crossprovider hermes hermes-loops-on-unresolved-pre-launch-gates-with
description: Hermes loops on unresolved pre-launch gates without escalation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-orchestration, stuck-loop-pattern]
---

When a pre-launch check sets a conditional gate (e.g., 'defer if upstream work affects this scope'), Hermes respawns the same session repeatedly without progress if the blocker condition remains unresolved or unclear. Needs explicit manual resolution or escalation to a human gate.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
