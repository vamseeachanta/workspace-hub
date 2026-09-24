---
name: crossprovider gemini adoption-idempotency-pattern-same-parent-no-op-d
description: Adoption idempotency pattern: same-parent no-op, different-parent fail
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [idempotency, state-management, edge-cases]
---

When adopting a child into a feature, check if parent is already set: same-parent → no-op (idempotent rerun safe); different-parent → hard exit 1 (integrity error); absent → insert normally. Prevents silent data corruption and makes re-runs safe.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
