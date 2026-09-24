---
name: crossprovider codex generated-configs-must-respect-existing-schema-p
description: Generated configs must respect existing schema path conventions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, convention, path-handling, generator]
---

If a spec schema documents that paths are relative to spec.yml, generated configs must preserve this; writing absolute paths breaks the contract. Generated code respects documented conventions rather than inventing new ones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
