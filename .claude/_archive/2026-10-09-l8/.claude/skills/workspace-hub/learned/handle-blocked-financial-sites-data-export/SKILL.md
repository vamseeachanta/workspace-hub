---
name: handle-blocked-financial-sites-data-export
description: Workflow for extracting data from blocked financial sites when browser automation is restricted
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["browser-automation", "financial-data", "workaround", "data-extraction"]
---

# Handle Blocked Financial Sites Data Export

When browser automation tools are blocked on financial sites (Fidelity, brokerages, banking portals), direct data extraction fails due to safety restrictions. Use fallback methods: request user copy/paste from the site, screenshot capture for OCR/manual reading, or CSV export via manual navigation. For sensitive account data, establish a clear repo separation pattern (private personal repo for data, separate repo for reusable algorithms) to minimize exposure while enabling analysis.