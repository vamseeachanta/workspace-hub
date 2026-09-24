---
name: crossprovider codex fencing-in-authorization-requires-api-level-enfo
description: Fencing in authorization requires API-level enforcement, not caller discipline
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, fencing, authorization]
---

Separate fence() call that's undocumented as required creates TOCTOU vulnerability between holds_venue() and side effect. Use decorator or required guarded_write() wrapper to enforce fencing immediately before mutation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
