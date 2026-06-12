---
name: crossprovider gemini template-consistency-variant-templates-must-shar
description: Template consistency: variant templates must share schema
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [template-design, schema-consistency, validation-coverage]
---

plan-template-minimal.md missing `## Plan Review Confirmation` block while plan-template.md has it causes validation divergence. All template variants (minimal, standard, extended) must include all required schema sections to prevent adoption of incomplete templates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
