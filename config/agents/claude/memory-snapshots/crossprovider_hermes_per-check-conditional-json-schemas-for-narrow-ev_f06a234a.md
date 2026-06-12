---
name: crossprovider hermes per-check-conditional-json-schemas-for-narrow-ev
description: Per-check conditional JSON schemas for narrow evidence validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [json-schema, validation, conditionals]
---

Use `allOf` with `if-then` conditionals to enforce different evidence requirements per canonical check ID, with reusable definitions for common payloads. This tightens validation without broadening the schema to all checks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
