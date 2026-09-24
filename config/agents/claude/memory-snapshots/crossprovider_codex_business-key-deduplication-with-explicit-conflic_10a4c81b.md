---
name: crossprovider codex business-key-deduplication-with-explicit-conflic
description: Business-key deduplication with explicit conflict classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, data-quality, ingestion]
---

Define deterministic business key (operator, fiscal_year, scope, normalized_metric_name, optional project_name) and partition ingestion results: accepted, duplicate (same key+value), conflict (same key, different value/citation), invalid. Handles second-order data quality without silent overwrites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
