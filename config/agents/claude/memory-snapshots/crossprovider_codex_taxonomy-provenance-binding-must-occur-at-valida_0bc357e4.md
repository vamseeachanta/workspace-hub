---
name: crossprovider codex taxonomy-provenance-binding-must-occur-at-valida
description: Taxonomy provenance binding must occur at validation, not query time
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, architecture, data-quality]
---

Accepting arbitrary `relevance_family` values at schema time and validating binding only at retrieval creates lookahead/query-time inversion risks. Binding (e.g., verify tags exist in registered taxonomy manifest) must happen at record acceptance. Stale sources (NIST explicitly warns it no longer updates) must be marked and excluded separately from freshness validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
