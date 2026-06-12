---
name: crossprovider hermes schema-enforcement-gap-fixtures-demonstrate-but-
description: Schema enforcement gap: fixtures demonstrate but don't guarantee downstream fields
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema, validation, contract]
---

Schema constraints don't enforce downstream-required evidence payload fields. Example: `checks[].evidence` in readiness-evidence-bundle schema is unconstrained optional object. Evidence fields demonstrated in fixtures/tests but not guaranteed by the JSON schema contract — downstream writers can't rely on field presence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
