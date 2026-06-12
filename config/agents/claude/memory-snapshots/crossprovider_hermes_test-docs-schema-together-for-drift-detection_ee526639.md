---
name: crossprovider hermes test-docs-schema-together-for-drift-detection
description: Test docs+schema together for drift detection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, documentation, schema-validation]
---

Schema validates individual objects; docs examples drift silently. Template README promises 'declare raw output path, compute environment' fields that schema doesn't enforce. Add doc-example validation tests: parse docs YAML fixtures, validate against schema, catch schema/doc divergence early.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
