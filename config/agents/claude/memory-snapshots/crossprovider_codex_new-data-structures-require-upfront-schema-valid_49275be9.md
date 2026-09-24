---
name: crossprovider codex new-data-structures-require-upfront-schema-valid
description: New data structures require upfront schema, validation, and integrity rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, validation, data-structure, plan-scope]
---

When a plan introduces new data structures (manifests, packages, formats), it must fully specify: schema structure, validation rules, integrity checks, version/compatibility handling, path normalization, and what makes one invalid. Deferring these to TDD creates ambiguity and forces rework.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
