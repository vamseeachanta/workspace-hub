---
name: crossprovider codex all-formula-inputs-and-intermediate-terms-must-b
description: All formula inputs and intermediate terms must be observable in output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [output-schema, transparency, auditability]
---

If a correction term or intermediate result is computed (e.g., downhole slippage before FVF), store and export it alongside the final result. Consumers need to reconstruct the formula and verify assumptions; discarding intermediate values blocks that. Include all Patterson inputs (diameter, SPM, clearance, viscosity) in the output schema, not just the final number.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
