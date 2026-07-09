---
name: crossprovider codex sidecar-cross-validation-must-be-bidirectional
description: Sidecar cross-validation must be bidirectional
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [validation-completeness]
---

Report checks that oil CSV fields are subset of sidecar fields, but not the reverse. A stale sidecar listing extra unrelated accepted factors still passes as complete and drops the caveat. Validate both direction: actual_fields == sidecar_factors, not just ⊆.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
