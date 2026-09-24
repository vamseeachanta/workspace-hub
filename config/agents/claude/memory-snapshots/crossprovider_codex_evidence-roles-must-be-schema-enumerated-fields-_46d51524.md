---
name: crossprovider codex evidence-roles-must-be-schema-enumerated-fields-
description: Evidence roles must be schema-enumerated fields, not implicit from placement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-typing, schema-enums, role-isolation]
---

Prose roles ('primary,' 'context,' 'comparison dependency') must be schema fields with enum values. Directory structure or file naming alone cannot enforce role isolation against schema-agnostic consumers; a solver report can relabel cross-solver evidence as 'context' and pass schema validation while violating role isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
