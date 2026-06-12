---
name: crossprovider codex partial-schema-loading-fails-on-required-fields
description: Partial schema loading fails on required fields
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, partial-loading, validation-gates]
---

Plans claiming DiffractionSpec.from_yaml() can load incomplete YAML templates and merge them post-load will fail: schema validation enforces required top-level fields (environment, frequencies, wave_headings, vessel|bodies) before overrides apply. Partial-load approaches need explicit merge strategy or field-by-field override path pre-plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
