---
name: extract-and-archive-tax-summary-data
description: Capture structured tax return summaries as YAML when PDF downloads are blocked or inaccessible
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "data-extraction", "pdf-workaround", "freetaxusa"]
---

# Extract and Archive Tax Summary Data

When PDF downloads from FreeTaxUSA are blocked by popups or automation restrictions, scrape the summary page HTML to extract all line items and save as structured YAML instead. Include year-over-year columns (e.g., 2024 vs 2025) to enable programmatic comparison. This preserves critical tax data even when file downloads fail, and the structured format is more queryable than PDFs for future analysis.