---
name: crossprovider codex dnv-ingest-script-reuse-library-for-privacy-safe
description: DNV ingest script reuse library for privacy-safe classifiers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dnv, reuse, privacy-guards, scripts-ingest]
---

When building new privacy-gated extractors, reuse these public interfaces: `build_dnv_extraction_shortlist()`, `build_dnv_extraction_batches()`, `source_label_denylist()`, `validate_source_label_commitments()`, `is_raw_source_key()`, `load_source_root_policy()`, `validate_source_label()`, and rank-preserving batch ID patterns. Replace literal source reference fields with opaque handles and commitment-only artifacts; do not reinvent privacy guards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
