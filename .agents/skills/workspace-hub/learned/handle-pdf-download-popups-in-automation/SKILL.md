---
name: handle-pdf-download-popups-in-automation
description: Recover when PDF download buttons open inaccessible popups; fall back to capturing structured data instead
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["browser-automation", "pdf-handling", "freetaxusa", "fallback-patterns"]
---

# Handle PDF Download Popups in Automation

When a website's PDF download opens in a popup window that automation can't access, don't loop on the download button. Instead: (1) take a screenshot to confirm popup is blocking, (2) pivot to capturing the page's structured data programmatically, (3) save to YAML/JSON with metadata, (4) create an issue documenting manual steps and file naming conventions. This preserves the data and provides a clear handoff for manual PDF retrieval.