---
name: crossprovider codex schema-validation-order-is-critical-with-multi-s
description: Schema validation order is critical with multi-source config merges
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, validation, config]
---

When merging CLI args, templates, and defaults into a config, validate AFTER the merge completes. Validating intermediate states can mask errors caught only after all sources are combined.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
