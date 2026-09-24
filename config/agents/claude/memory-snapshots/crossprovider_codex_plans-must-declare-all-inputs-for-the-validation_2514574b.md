---
name: crossprovider codex plans-must-declare-all-inputs-for-the-validation
description: Plans must declare all inputs for the validations they perform
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, correctness, input-contracts]
---

If a plan claims to fail-close on schema/gate_status/row consistency, those inputs must be explicitly listed and present in the pipeline. Deriving fields from optional sources or assuming they are implicitly available breaks correctness; all validation requirements must map to declared inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
