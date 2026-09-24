---
name: crossprovider codex off-topic-contamination-in-data-collections-brea
description: Off-topic contamination in data collections breaks downstream pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-hygiene, content-filter, pipeline-robustness]
---

Non-standard PDFs (vendor catalogs, screenshots, classifieds) mixed into a standards collection do not degrade gracefully—they actively break ingest and analysis pipelines. Identify and quarantine off-topic content with a skip reason, queue for manual review; do not ingest as stubs or placeholders.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
