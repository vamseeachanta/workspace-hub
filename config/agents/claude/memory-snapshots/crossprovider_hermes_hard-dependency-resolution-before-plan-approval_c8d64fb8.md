---
name: crossprovider hermes hard-dependency-resolution-before-plan-approval
description: Hard dependency resolution before plan approval
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-management, approval-gates, risk-mitigation]
---

If a plan depends on an upstream decision (model selection, architecture choice, config decision), that dependency must be RESOLVED before plan approval, not merely filed as a separate issue. A scaffold with "no decision yet" blocks downstream plan approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
