---
name: crossprovider codex reconciliation-schemas-need-stable-identity-prov
description: Reconciliation schemas need stable identity + provenance, not counts alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, ingest, reconciliation]
---

Count-only reconciliation is insufficient for downstream ingestion. Schemas must include content-identity fields (SHA-256 hash, doc_key), source provenance (catalog key, research-index key), and integration fields (wiki_refs, extraction_status, promotion_status, reviewer_disposition) to support backfill and promotion workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
