---
name: crossprovider hermes multi-schema-jsonl-extractions-need-deduplicatio
description: Multi-schema JSONL extractions need deduplication before curation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-extraction, data-quality, deduplication, schema-validation]
---

The worked_examples.jsonl contained two distinct schemas mixed (raw OCR text vs. structured records with expected values). Deduplication found 156 duplicates in 423 records (37% dedup rate). Schema separation was required before filtering for test vector quality. Recommendation: validate schema consistency and deduplicate BEFORE downstream curation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
