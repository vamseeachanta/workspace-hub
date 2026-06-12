---
name: crossprovider hermes determinism-must-be-operationalized-with-explici
description: Determinism must be operationalized with explicit rules, not asserted
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, acceptance-criteria, determinism, output-contract]
---

Plans asserting "deterministic output" without defining rules for ordering, float formatting, whitespace normalization, attribute ordering, SVG ID generation, or sorting are underspecified. Operationalize determinism with concrete examples or test-enforced rules. Generic "deterministic" is not reviewable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
