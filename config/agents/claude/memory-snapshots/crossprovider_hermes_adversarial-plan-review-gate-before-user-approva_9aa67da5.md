---
name: crossprovider hermes adversarial-plan-review-gate-before-user-approva
description: Adversarial plan-review gate before user approval
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review, adversarial-review, workflow, quality-gate]
---

Plans reach `status:plan-review` only after adversarial review from at least two independent providers produces no MAJOR findings. Plan bodies track review-artifact references; update pointers during revisions to avoid conflicting retrieval paths. Self-review during build is not the gate.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
