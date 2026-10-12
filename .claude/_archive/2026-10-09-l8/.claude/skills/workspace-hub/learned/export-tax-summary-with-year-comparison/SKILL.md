---
name: export-tax-summary-with-year-comparison
description: Extract and structure tax return data into YAML format for year-over-year comparison across different filing products
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-workflow", "data-export", "year-comparison", "financial-records"]
---

# Export Tax Summary with Year-over-Year Comparison

When tax preparation tools block automated PDF downloads (via popups or new tabs), capture the structured summary data from the web interface instead. Export line-item data to YAML format with both current and prior-year columns for programmatic comparison. This approach is filing-product-agnostic and survives workflow changes—if next year uses a different tax service, the prior-year YAML remains instantly comparable without manual re-entry.