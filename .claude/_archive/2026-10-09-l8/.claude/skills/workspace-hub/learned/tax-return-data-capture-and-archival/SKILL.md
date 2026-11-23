---
name: tax-return-data-capture-and-archival
description: Capture structured tax return summaries as YAML for year-over-year comparison, with fallback to manual PDF download and relocation when automation fails
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-workflows", "data-archival", "pdf-handling", "structured-data"]
---

# Tax Return Data Capture and Archival

When automating tax return downloads from web-based tax software (e.g., FreeTaxUSA), capture the summary page data as structured YAML with year-over-year columns instead of relying solely on PDFs. This enables programmatic comparison across tax years and products. If PDF downloads open in popups the automation cannot access, parse the summary HTML and save as YAML, then create a manual download issue. After manual download to the Downloads folder, use file operations to rename (with year/form-type) and relocate to the appropriate archive path (`_finance/tax/YEAR/personal/`).