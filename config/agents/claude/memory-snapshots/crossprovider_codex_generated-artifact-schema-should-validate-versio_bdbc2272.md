---
name: crossprovider codex generated-artifact-schema-should-validate-versio
description: Generated artifact schema should validate version contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, schema, data-integrity]
---

When loading structured data (schemas, allowlists, manifests), validate the version/type field against expected values rather than assuming compatibility. Mismatches between parent and row schemas can silently corrupt data pipelines if left unvalidated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
