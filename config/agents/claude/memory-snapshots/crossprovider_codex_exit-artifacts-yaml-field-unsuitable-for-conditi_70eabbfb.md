---
name: crossprovider codex exit-artifacts-yaml-field-unsuitable-for-conditi
description: Exit_artifacts YAML field unsuitable for conditionally-required outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, yaml-schema, conditional-logic]
---

Using exit_artifacts to gate conditional deliverables (e.g., feature-decomposition.yaml only for type:feature) fails because exit_stage.py treats all exit_artifacts as unconditional. Use feature_notes blocks or explicit downstream guards instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
