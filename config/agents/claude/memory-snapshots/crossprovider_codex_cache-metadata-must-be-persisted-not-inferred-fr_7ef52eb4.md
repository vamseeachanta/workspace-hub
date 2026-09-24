---
name: crossprovider codex cache-metadata-must-be-persisted-not-inferred-fr
description: Cache metadata must be persisted, not inferred from filename suffix
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [caching, http, cache-keys, content-negotiation]
---

Inferring cached content-type from the cache filename suffix (e.g., no suffix → HTML, .pdf → PDF) breaks on extensionless URLs or parametric queries (e.g., /download?id=123). Persist normalized content-type and final URL alongside cached bytes; use stored metadata on cache hits, not guessed type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
