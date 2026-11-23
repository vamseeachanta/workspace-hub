---
name: tax-pdf-download-workaround
description: Handle FreeTaxUSA PDF download popups that block automation by capturing structured data and manual download workflow
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "pdf", "automation", "workaround"]
---

# Tax PDF Download Workaround

When PDF download buttons open popup windows that block automation, skip the automation and use manual download + rename workflow. Save PDFs to `_finance/tax/YYYY/personal/freetaxusa-pdfs/` with standardized names. Simultaneously capture structured summary data (YAML format with prior-year comparison) to preserve programmatic access to tax line items for year-over-year analysis and record-keeping independent of PDF retrieval success.