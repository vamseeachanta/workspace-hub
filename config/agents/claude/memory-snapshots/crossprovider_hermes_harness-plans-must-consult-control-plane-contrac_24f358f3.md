---
name: crossprovider hermes harness-plans-must-consult-control-plane-contrac
description: Harness plans must consult CONTROL_PLANE_CONTRACT, config/agents, .claude/rules
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [harness, retrieval-contract, approval-gate]
---

Plans labeled cat:harness fail approval if they omit mandatory retrieval of CONTROL_PLANE_CONTRACT.md, config/agents/, and .claude/rules/. These define the harness contracts, approval gates, and execution model. Omission blocks approval even if implementation is sound.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
