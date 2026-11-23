---
name: handle-popup-blocked-pdf-downloads
description: Recover from automation-blocking PDF popups by capturing page data and escalating to manual download
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["automation", "debugging", "pdf", "web-scraping"]
---

# Handle Popup-Blocked PDF Downloads

When automating web forms that open PDFs in popup viewers (common in tax/financial software), the automation cannot access popup content. Instead of looping on failed downloads: (1) detect the popup block by attempting the action and checking for new tabs/files, (2) screenshot to confirm a popup occurred, (3) pivot to scraping the underlying summary data from the main page, (4) save the data to structured format, (5) create a GitHub issue documenting which PDFs need manual download and their reference IDs for human follow-up.