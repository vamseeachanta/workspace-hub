---
name: crossprovider codex verification-queue-as-a-metadata-artifact
description: Verification queue as a metadata artifact
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, verification, metadata]
---

Create a `_verification-queue.csv` listing all provisional+raw tables with code_id, table_id, source_pdf, source_page, parse_status, caption. This decouples data generation (which marks tables provisional) from verification (which checks them later). Queue row count should equal table count exactly — use as an invariant check.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
