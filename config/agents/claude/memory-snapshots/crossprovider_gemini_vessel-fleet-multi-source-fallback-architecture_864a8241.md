---
name: crossprovider gemini vessel-fleet-multi-source-fallback-architecture
description: Vessel fleet multi-source fallback architecture
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-architecture, fallback-pattern, worldenergydata]
---

Drilling fleet collectors employ a tiered fallback: live web scrape → pre-collected Puppeteer scrape JSON → KNOWN_VESSELS from config. Best source (most records) wins per operator. Generalizable pattern for data integration across multiple vendors/formats.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
