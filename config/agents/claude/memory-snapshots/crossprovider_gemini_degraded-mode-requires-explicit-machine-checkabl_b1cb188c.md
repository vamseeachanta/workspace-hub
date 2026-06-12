---
name: crossprovider gemini degraded-mode-requires-explicit-machine-checkabl
description: Degraded mode requires explicit machine-checkable approval
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [fault-tolerance, user-in-loop]
---

When a provider is unavailable, silence is not approval. Require explicit `approved_by`, `approval_scope`, `missing_providers` fields in the evidence YAML to proceed in degraded mode; runtime validation checks these fields before gate passage.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
