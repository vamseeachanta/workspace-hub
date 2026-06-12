---
name: crossprovider hermes adversarial-review-blocks-plan-implementation-mu
description: Adversarial review blocks plan implementation, must clear MAJOR findings first
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plans, review-gates, approval-workflow]
---

Issues #2726–#2729 all blocked on unresolved adversarial MAJOR verdicts across Claude/Codex/Gemini. Plans cannot move from `status:plan-review` to `status:plan-approved` or implementation without fresh review clearing all MAJOR findings. Skipping this gate produces silent defects.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
