---
name: crossprovider hermes implementation-acceptance-gates-require-explicit
description: Implementation acceptance gates require explicit schema tests, not inference from artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [acceptance, schema, testing]
---

Whether generated artifacts contain approved-plan fields (code_id, publisher, cross_links) is not self-evident. Acceptance must include explicit tests validating field presence, not just running validator.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
