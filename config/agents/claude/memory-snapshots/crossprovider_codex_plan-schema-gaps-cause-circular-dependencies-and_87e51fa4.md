---
name: crossprovider codex plan-schema-gaps-cause-circular-dependencies-and
description: Plan schema gaps cause circular dependencies and unvalidatable output
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan, schema, sequencing, validation]
---

WRK-205 skills graph plan had frontmatter generation depending on frontmatter existing, and domain/category mapping undefined; these gaps forced sequence inversion and left coverage unspecified. Always define strict schema (frontmatter keys, edge types, cardinality, validation rules) BEFORE execution sequencing; unspecified schemas prevent both scripted generation and post-hoc validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
