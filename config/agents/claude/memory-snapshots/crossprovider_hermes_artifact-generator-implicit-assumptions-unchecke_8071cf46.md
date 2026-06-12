---
name: crossprovider hermes artifact-generator-implicit-assumptions-unchecke
description: Artifact generator implicit assumptions unchecked at build time
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-generation, validation, schema]
---

Chart generation duplicates, rounding inconsistencies, and variable-count mismatches persist across sessions, suggesting artifact generator has implicit assumptions (e.g., chart layout, decimal places, which fields to plot) not validated by tests. Need explicit test oracle (manifest of expected artifact structure) or build-time schema validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
