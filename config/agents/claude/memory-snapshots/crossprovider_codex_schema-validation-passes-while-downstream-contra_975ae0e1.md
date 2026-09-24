---
name: crossprovider codex schema-validation-passes-while-downstream-contra
description: Schema validation passes while downstream contracts remain incomplete
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, testing, contracts, edge-cases]
---

Registry schema accepts `raw_roots: []` syntactically but templates and factory code assume real roots; validators catch syntax errors but miss semantic boundary mismatches. Test coverage must explicitly span edge states (empty collections, disabled modes, fail-closed paths) that pass validation but break downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
