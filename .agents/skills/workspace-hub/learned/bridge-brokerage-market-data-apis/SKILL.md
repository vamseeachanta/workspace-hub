---
name: bridge-brokerage-market-data-apis
description: Handle ticker symbol mismatches between brokerage exports and market data APIs
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["data-integration", "api-bridging", "market-data"]
---

# Bridge Brokerage and Market Data APIs

When ingesting brokerage data (e.g., Fidelity CSV) and fetching live prices from market APIs (e.g., Yahoo Finance), ticker symbols often differ. Create a centralized `TICKER_MAP` dict to alias brokerage symbols to API symbols (e.g., `BRKB → BRK-B`). Also extend API queries with a longer period window (e.g., `5d` instead of `1d`) to handle weekends/holidays returning empty data. Apply the mapping at the ingest layer before price-fetch calls.