---
name: crossprovider gemini multi-source-fallback-collection-with-record-cou
description: Multi-source fallback collection with record-count selection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-pipeline, fallback-strategy, collection]
---

Implement fallback chains for data collection (live web scrape → pre-collected JSON → hardcoded KNOWN_VESSELS), ranking sources by recency and accuracy. Select the source that returns the most records per operator. Use dynamic importlib.import_module() to load operator configs, avoiding hard-coded lists.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
