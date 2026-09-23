---
name: crossprovider codex hard-schema-version-gates-require-bidirectional-
description: Hard schema version gates require bidirectional test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-24
  tags: [schema-migration, test-coverage, equality-matrix, regression-prevention]
---

When a collector updates to emit schema N+1 but the builder still rejects non-N with hard equality checks (e.g., `schema_version == 4`), production data flows silently regress to MISSING-EVIDENCE while tests pass. Fix by accepting schema ranges and testing both the new emitter output AND the builder's acceptance path for the new schema in the same test suite.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
