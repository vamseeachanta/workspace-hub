---
name: crossprovider codex preserve-source-and-derived-values-separately-in
description: Preserve source and derived values separately in catalogs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [catalog, provenance, audit-trail]
---

Store both source values (e.g., rounded 16 kft/s from workbook) and computed values (16,299.8 ft/s). Silently substituting one for the other blocks auditing and makes errors hard to trace.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
