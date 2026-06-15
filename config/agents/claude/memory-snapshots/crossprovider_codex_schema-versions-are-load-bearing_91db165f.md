---
name: crossprovider codex schema-versions-are-load-bearing
description: Schema versions are load-bearing
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema, versioning, provenance, data-integrity]
---

Equality matrix schema v2 (no provenance block) vs v3 (has provenance, freshness tracking) are not interchangeable. Stale tree at v2 silently produces data-loss when collected output expects v3.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
