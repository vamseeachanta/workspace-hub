---
name: crossprovider codex separate-source-identity-from-deduplication-key-
description: Separate source identity from deduplication key in multi-source ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-modeling, ingestion, multi-source, deduplication]
---

When building corpora from mirrored sources (e.g., og-asme + og-raw-asme), use root-independent deduplication keys (publisher+designation+edition+fingerprint) while preserving source-dependent identity fields (source_id per root). This allows tracking source provenance while avoiding duplicate content rows in the final manifest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
