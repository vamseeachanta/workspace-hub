---
name: crossprovider hermes schema-enforcement-gaps-between-docs-and-code-ca
description: Schema enforcement gaps between docs and code cause silent conformance failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema, testing, conformance]
---

Documentation marked 'added' field as required but code doesn't enforce it; tests pass despite missing enforcement. Add tests that compare schema docs against code enforcement; treat divergence as a defect class.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
