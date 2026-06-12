---
name: crossprovider hermes validator-weakness-surface-level-checks-miss-con
description: Validator weakness: surface-level checks miss content correctness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, testing, structured-artifacts]
---

Validators that only check formatting (headings, patterns, forbidden strings) don't catch content-correctness bugs in structured artifact systems. Must also verify: manifest contents match report rows, report contents match generated state, and schema constraints (tool fields, required columns). Adversarial review in llm-wiki #79 caught manifest/report mismatches passing validation when only surface checks were enabled.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
