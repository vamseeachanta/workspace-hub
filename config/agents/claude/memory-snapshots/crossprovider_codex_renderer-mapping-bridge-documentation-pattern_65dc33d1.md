---
name: crossprovider codex renderer-mapping-bridge-documentation-pattern
description: Renderer mapping bridge documentation pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, schema, communication]
---

When documentation schema is richer than actual renderer capabilities, add explicit 'Renderer Mapping Note' sections showing the gap and guidance for encoding concepts into supported fields. Example: WRK-1242 documented structured author lists with roles, but renderer accepted only scalar author—mapping notes showed how to encode multiple signatories into change_log descriptions instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
