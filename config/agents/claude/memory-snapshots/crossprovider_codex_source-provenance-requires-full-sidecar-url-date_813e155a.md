---
name: crossprovider codex source-provenance-requires-full-sidecar-url-date
description: Source provenance requires full sidecar (URL + date + quote), not just ID field
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [provenance, data-integrity, source-tracking, acceptance-criteria]
---

A `source_id` field alone is insufficient and unsafe when multiple sources use different bases (e.g., Shell $1.7B total vs Talos $450-500M net). Provenance sidecar must include publisher, release date, access date, source quote/excerpt, and claim-level mapping. Dummy IDs pass tests but allow unattributed commercial terms to ship.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
