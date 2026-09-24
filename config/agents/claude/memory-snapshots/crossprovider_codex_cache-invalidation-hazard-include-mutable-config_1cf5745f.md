---
name: crossprovider codex cache-invalidation-hazard-include-mutable-config
description: Cache invalidation hazard: include mutable config in cache key
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, caching, state-management]
---

When per-call configuration affects behavior (e.g., fixture path in provider initialization) but caching is keyed only by static identity (e.g., provider name), subsequent calls with different config hit stale cache. Solution: include mutable config in cache identity or eliminate mutable component state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
