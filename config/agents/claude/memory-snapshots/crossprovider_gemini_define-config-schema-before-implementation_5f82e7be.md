---
name: crossprovider gemini define-config-schema-before-implementation
description: Define config schema before implementation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [config, schema, design]
---

Leaving schema unspecified ("routing-rules.yaml is declarative policy" without defining keys/structure) guarantees implementation guessing, parse errors, and overlap with existing configs. Draft minimum viable schema in the plan.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
