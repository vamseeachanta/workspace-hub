---
name: crossprovider hermes conditional-promotion-gates-must-be-schema-enfor
description: Conditional promotion gates must be schema-enforced, not test-only
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-design, TDD-anti-pattern, contract-enforcement]
---

Documenting 'public outputs require provenance + license + legal + sanitization + owner-review gates' is insufficient. Schema must conditionally enforce the full gate set: if output_residency='public', then require all 5 gate names in promotion_gates enum. Test-only checks (non-empty gates) allow seed fixtures to use arbitrary gate names and still pass validation, leaving the contract fail-open in production.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
