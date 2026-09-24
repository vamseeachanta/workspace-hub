---
name: crossprovider codex registry-key-namespacing-for-external-data-impor
description: Registry key namespacing for external data imports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-import, design-pattern, schema]
---

When building registries from scraped or external sources, use namespaced keys (e.g., 'CV_' + identifier) instead of raw identifiers to ensure uniqueness across imports and resilience to data updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
