---
name: handle-browser-automation-financial-site-blocks
description: Workflow for working around Chrome extension blocks on financial sites during data collection tasks
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["browser-automation", "data-collection", "fidelity", "workarounds"]
---

# Handle Browser Automation Blocks on Financial Sites

When browser automation tools are blocked on financial domains (Fidelity, brokerages, etc.) due to safety restrictions, use fallback data collection methods: screenshot capture for OCR/image reading, manual CSV export from the site's UI, copy-paste of table data into chat, or ask user to download files locally. Never attempt to bypass security blocks—instead, pivot to human-in-loop data transfer (screenshot, export, paste) and process the data after receipt.