---
name: crossprovider hermes metadata-first-bulk-wiki-ingestion-at-scale
description: Metadata-first bulk wiki ingestion at scale
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [wiki, batch-processing, scaling]
---

For 10K+ document ingestion, use metadata-first approach (titles, topics) instead of full-text extraction to avoid 5-min timeouts. Implement checkpoint-based resume with .checkpoint.jsonl tracking processed IDs. Use 100 records/batch achieving ~400 records/10s throughput. Update index.md after each batch, not per-record.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
