---
name: crossprovider gemini approval-after-revert-has-narrow-validity-window
description: Approval after revert has narrow validity window
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [policy-design, correctness, specifications]
---

In bypass/rollback policies, later approval of a bypassed change only counts if the original SHA remains unreverted and resolvable. If the SHA is already reverted, later approval does not override revert.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
