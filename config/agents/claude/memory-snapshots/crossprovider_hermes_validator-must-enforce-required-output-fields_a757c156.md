---
name: crossprovider hermes validator-must-enforce-required-output-fields
description: Validator must enforce required output fields
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-validation, acceptance-criteria, test-completeness]
---

Validators should REQUIRE acceptance-critical fields in output JSON schema (e.g., `domain_deltas`, `concept_watchlist`), not just validate them if present. Absence of required fields means incomplete/unsafe output but passes validation if validation only checks 'if present'. Use strict schema enforcement.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
