---
name: crossprovider codex field-mappings-need-visible-formulas-not-just-so
description: Field mappings need visible formulas, not just source→sink entries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, field-mapping, data-transformation]
---

Plans mapping source data to output fields hide incomplete implementations when formulas are absent. Example: 'strake_modules.length_m → VariableData[0].LayerThickness' lacks the scaling/aggregation logic. Mapping tables must include explicit formulas or references, or tests can pass while data transformation is incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
