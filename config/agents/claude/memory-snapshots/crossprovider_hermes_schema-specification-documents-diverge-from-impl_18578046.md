---
name: crossprovider hermes schema-specification-documents-diverge-from-impl
description: Schema specification documents diverge from implementation artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation-debt, schema-staleness, architecture-drift]
---

Specification .md files frequently list fields never emitted (e.g., source_scope, backlinks) and omit fields present in actual output (e.g., is_curated), signaling staleness. Regenerate and diff spec against emitted artifacts on each implementation change to keep spec authoritative.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
