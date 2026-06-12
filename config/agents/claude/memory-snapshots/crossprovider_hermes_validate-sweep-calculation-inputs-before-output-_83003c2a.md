---
name: crossprovider hermes validate-sweep-calculation-inputs-before-output-
description: Validate sweep calculation inputs before output generation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-calculations, input-validation, sweep-calculations]
---

Engineering sweep/parameter calculations must validate non-empty inputs (speeds, angles, rudder angles) at validation time and raise ValueError; generating outputs on empty inputs is an error condition, not a graceful stub.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
