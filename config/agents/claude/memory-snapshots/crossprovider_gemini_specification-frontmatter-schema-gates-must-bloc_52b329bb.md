---
name: crossprovider gemini specification-frontmatter-schema-gates-must-bloc
description: Specification frontmatter schema gates must block execution
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [schema-validation, workflow-gates, work-queue]
---

Medium/complex work items should not reach execution without `plan_reviewed: true` in frontmatter. Earlier iteration allowed items through without this gate, now patched in wrapper guards. Schema validation must be enforced at workflow entry point, not as best-effort audit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
