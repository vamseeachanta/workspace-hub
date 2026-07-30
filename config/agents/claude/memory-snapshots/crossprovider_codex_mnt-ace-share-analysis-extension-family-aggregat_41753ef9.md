---
name: crossprovider codex mnt-ace-share-analysis-extension-family-aggregat
description: /mnt/ace share analysis: extension-family aggregation, not unbounded crawl
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [/mnt/ace, share-inventory, data-ingestion]
---

/mnt/ace holds 3M+ files/1.2 TB indexed in assets.json. Avoid unbounded find/du operations; aggregate by extension family (text, spreadsheet, document, CAD, simulation, database) with size and ingestion-ease scoring. Current llm-wiki ingestion is ~0%; future bulk-ingestion requires explicit public/private sanitization before corpus load.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
