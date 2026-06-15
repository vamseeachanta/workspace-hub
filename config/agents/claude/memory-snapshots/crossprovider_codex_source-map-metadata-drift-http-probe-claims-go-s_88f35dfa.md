---
name: crossprovider codex source-map-metadata-drift-http-probe-claims-go-s
description: Source map metadata drift: HTTP probe claims go stale
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [source-maps, metadata, testing]
---

Source maps record HTTP behavior metadata (e.g., 'HEAD returned 404, GET returned 200') that can drift as target URLs change; tests using fake runners won't catch actual reachability regressions. Validate probe claims live or accept they are historical, not current.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
