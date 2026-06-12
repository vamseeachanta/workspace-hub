---
name: crossprovider hermes semantic-equivalence-validation-for-domain-code-
description: Semantic equivalence validation for domain code generation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-generation, testing, validation, domain-specific]
---

When proving generated domain-specific code is equivalent to native solver formats, use fixture-backed validation combined with a semantic diff taxonomy that explicitly defines which differences are acceptable (e.g., field ordering, unit representation, precision). Enforcing taxonomy rules against real artifacts prevents silent drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
