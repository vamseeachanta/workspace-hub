---
name: crossprovider codex schema-validation-universe-must-be-defined-indep
description: Schema validation universe must be defined independently from coverage scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-validation, scope-definition, validation-hazard]
---

Plans that validate records against a schema must precisely define which records are in-scope for validation vs. which participate in coverage indexing. A record cannot both require a field for in-scope status and also be valid-for-audit when the field is missing. Separate validation universe from coverage universe.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
