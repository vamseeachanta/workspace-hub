---
name: multi-format-transaction-parser
description: Parse and consolidate financial transaction data across multiple CSV formats and years
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["data-processing", "finance", "csv-parsing", "historical-data"]
---

# Multi-Format Transaction Parser

When analyzing financial data spanning multiple years/sources, transaction CSV formats often differ (column names, date formats, transaction types). Build an adaptive parser that detects format variations, handles schema mismatches gracefully, and consolidates into a unified dataset. Use pandas with conditional logic to map columns by position or fuzzy matching, then validate totals across years to catch parsing errors.