---
name: crossprovider codex unit-and-format-conversions-embedded-in-field-ma
description: Unit and format conversions embedded in field maps create silent correctness risks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, schema, unit-handling]
---

Plans that convert between units (kg/m³ to te/m³) or assume field formats without explicit validation in tests create correctness bugs that surface only at runtime or integration. A plan may specify 'divide by 1000' in documentation but tests never validate the conversion actually occurred or that the output schema expects the target unit. Always require tests that verify unit/format correctness at the schema boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
