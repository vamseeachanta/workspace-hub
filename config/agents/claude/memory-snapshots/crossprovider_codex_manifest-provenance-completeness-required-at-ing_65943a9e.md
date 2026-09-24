---
name: crossprovider codex manifest-provenance-completeness-required-at-ing
description: Manifest/provenance completeness required at ingest boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, data-pipeline, manifest-design, reproducibility]
---

Data pipelines must capture raw source URLs, response headers, SHA256 hashes, and timestamps at fetch time and embed them in provenance manifests. Without these at ingest, later refreshes can overwrite raw manifests, leaving curated outputs orphaned with only stale path pointers. Quality counts, parser failures, and missing fields must also be counted in manifest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
