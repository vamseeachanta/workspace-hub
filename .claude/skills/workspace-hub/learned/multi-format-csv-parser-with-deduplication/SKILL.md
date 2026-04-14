---
name: multi-format-csv-parser-with-deduplication
description: Parse brokerage CSV exports that exist in multiple formats with overlapping data across files
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["data-ingestion", "csv-parsing", "deduplication", "brokerage-data"]
---

# Multi-Format CSV Parser with Deduplication

When ingesting brokerage data across multiple files or format versions, first map all edge cases (header variations, footer disclaimers, BOM markers). Auto-detect format from header row. Strip footers and BOM before parsing. Build a deduplication key (e.g., date + ticker + quantity + price) to merge overlapping transaction rows across files. Validate final dataset against user-stated holdings to catch parsing errors early.