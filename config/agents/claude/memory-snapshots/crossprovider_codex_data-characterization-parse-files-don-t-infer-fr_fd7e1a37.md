---
name: crossprovider codex data-characterization-parse-files-don-t-infer-fr
description: Data characterization: parse files, don't infer from UI
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-ingestion, verification, methodology]
---

Download and directly parse data files (openpyxl for Excel, pdftotext for PDF) to extract exact column headers, units, layout. Don't rely on web-page labels or rendered views; workbooks have formatted empty rows that skew coverage, headers vary between language versions, and URLs become stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
