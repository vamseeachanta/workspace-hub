---
name: multi-format-csv-detection-and-deduplication
description: Detect and handle multiple CSV format versions from the same data source; deduplicate records across format variants
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["csv", "data-ingestion", "format-detection", "deduplication", "brokerage-data"]
---

# Multi-Format CSV Detection and Deduplication

When ingesting CSVs from sources that evolve formats over time (e.g., Fidelity exports with old vs. new column orders), detect format from header structure rather than filename. The same year/period can exist in both formats with identical transactions. Use column position and presence of distinguishing headers (e.g., 'Account Number' only in new format) as discriminators. Build a unified parser that normalizes both formats to a canonical schema, then deduplicate by transaction fingerprint (date, ticker, quantity, price) across all input files.