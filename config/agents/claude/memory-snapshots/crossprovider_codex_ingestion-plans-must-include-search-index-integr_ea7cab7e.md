---
name: crossprovider codex ingestion-plans-must-include-search-index-integr
description: Ingestion plans must include search-index integration or content is not discoverable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ingestion-pipeline, search-integration, deliverable-scope]
---

#2103 (BEMRosetta/AQWA) plan proposed content but did not modify `search-wiki.py` which hardcodes `PRODUCTS = [...]` and per-product `index.json` loading. As written, new content would not surface in search, making the deliverable unachievable. Ingestion plans must name the search entry point and specify integration path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
