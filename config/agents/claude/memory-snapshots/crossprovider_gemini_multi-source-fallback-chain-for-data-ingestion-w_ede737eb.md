---
name: crossprovider gemini multi-source-fallback-chain-for-data-ingestion-w
description: Multi-source fallback chain for data ingestion with graceful degradation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-engineering, resilience, collection-pattern, fallback-chain]
---

Design data collection pipelines with ranked source precedence: (1) live web scrape (if enabled), (2) pre-cached/scraped JSON (if available), (3) hardcoded known-vessel fallback (always available). Select winner by cardinality (most records). Enables operational flexibility—different environments/modes use different sources without code changes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
