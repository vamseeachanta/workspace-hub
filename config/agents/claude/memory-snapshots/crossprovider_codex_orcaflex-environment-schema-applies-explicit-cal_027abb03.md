---
name: crossprovider codex orcaflex-environment-schema-applies-explicit-cal
description: OrcaFlex environment schema applies explicit calm defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, orcaflex, defaults, digitalmodel]
---

When metocean data is absent, the OrcaFlex environment schema populates fields with explicit calm-water defaults (wave 0m, period 8s, current 0 m/s, wind 0 m/s at 10m, current profile [[0, 1.0]]) rather than null or optional values. Converters and generators must emit these explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
