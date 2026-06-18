---
name: crossprovider codex private-source-encoding-requires-resolver-map-sp
description: Private source encoding requires resolver map specification, not just handle format
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [design, data-security, specification-completeness]
---

When designing opaque source handles (e.g., source-ref:*), specify not just the encoding scheme but also how the private resolver map is stored, versioned, validated, and accessed during backfill. One-sided encoding without the resolver map is underspecified for implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
