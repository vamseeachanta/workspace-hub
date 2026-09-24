---
name: crossprovider codex schema-composition-requires-explicit-field-name-
description: Schema composition requires explicit field-name scoping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, integration-testing, cross-repo-coordination]
---

When composing multiple schemas (report-evidence-bundle, execution-manifest), overlapping field names like `source_class` can silently collide with different semantics. Require integration tests proving field definitions don't redefine across schemas, and rename fields explicitly if semantics differ (e.g., `source_legal_class` vs `source_class`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
