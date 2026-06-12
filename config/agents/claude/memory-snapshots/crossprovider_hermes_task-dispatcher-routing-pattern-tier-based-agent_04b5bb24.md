---
name: crossprovider hermes task-dispatcher-routing-pattern-tier-based-agent
description: Task dispatcher routing pattern: tier-based agent scoring with keyword signal
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [task-dispatch, routing-logic, agent-selection]
---

Implement task-to-agent routing by scoring agents against a tier-preference matrix (simple/standard/complex/reasoning) plus keyword signal matching (e.g., boost for Hermes on data-heavy tasks). Output includes recommended agent, model, provider, confidence score, and rationale. Makes routing logic transparent and auditable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
