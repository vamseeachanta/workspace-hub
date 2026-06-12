---
name: crossprovider hermes durable-promotion-evidence-gates-over-self-asser
description: Durable promotion evidence gates over self-assertion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, privacy, validation-gates]
---

Boolean flags + freeform text for 'this is public' is bypassable; actor can flip output_residency to public_llm_wiki + set release gates true without durable promotion record. Require references to approval/promotion artifacts (e.g., GitHub issue comment, audit log) as the gate, not self-asserted booleans.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
