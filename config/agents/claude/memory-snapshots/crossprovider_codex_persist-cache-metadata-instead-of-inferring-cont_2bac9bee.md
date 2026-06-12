---
name: crossprovider codex persist-cache-metadata-instead-of-inferring-cont
description: Persist cache metadata instead of inferring content-type from filename
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [caching, content-type, cache-coherence]
---

Disk caches that infer content-type from filename suffix (e.g., extensionless URL → .html) misclassify on mismatch (e.g., /download?id=123 returning PDF). Must store normalized content-type and final URL alongside cached bytes, then use that on cache hits instead of guessing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
