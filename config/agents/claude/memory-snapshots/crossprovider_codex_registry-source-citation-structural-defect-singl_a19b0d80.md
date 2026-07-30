---
name: crossprovider codex registry-source-citation-structural-defect-singl
description: Registry source-citation structural defect: single source_url + multi-field attributes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [registry-schema, source-citation, data-governance]
---

When a registry record stores attributes originating from different sources (e.g., `api_gravity_min/max` from source A, `api_gravity` from source B) under a single `source_url` field, the citation becomes ambiguous — readers cannot distinguish which source authored which field. Ayoluengo example: stored 20–39° API range (technical guide) + 37° API point (LGO operator page) both citing the archived LGO URL. Fix: add structured multi-source support (caveat_fields, source_arrays, multi-ref fields) or restrict to single-source records.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
