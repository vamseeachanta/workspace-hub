---
name: crossprovider codex data-provenance-must-capture-http-metadata-hashe
description: Data provenance must capture HTTP metadata, hashes, and point-in-time manifest snapshots
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [data-governance, provenance, reproducibility]
---

Data systems claiming reproducibility need to store not just input paths but raw source URLs, SHA256 hashes, HTTP response headers, output hashes, and raw-manifest snapshots. Without these, later source refreshes silently overwrite upstream data while leaving curated outputs orphaned with stale path pointers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
