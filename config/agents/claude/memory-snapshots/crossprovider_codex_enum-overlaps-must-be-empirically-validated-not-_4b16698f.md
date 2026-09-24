---
name: crossprovider codex enum-overlaps-must-be-empirically-validated-not-
description: Enum overlaps must be empirically validated, not asserted disjoint
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enum-design, testing, defect-class]
---

Claiming that control-plane verification states and page-trust parse statuses are separate is insufficient; reused values like 'rejected' must be tested to confirm they don't collide at the string level. Validation must check exact set membership against existing vocabulary, not just assume prose boundaries hold.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
