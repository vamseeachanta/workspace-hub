---
name: crossprovider codex html-report-output-silently-truncates-while-json
description: HTML report output silently truncates while JSON contains full data, masking defects
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, manifest-builders, reporting, silent-truncation]
---

maritime_regulatory_source_manifest.html caps output at 200 rows while manifest.jsonl has 1074, creating mismatch. Silent truncation hides whether all rows are correctly classified. Either include all rows in HTML (with pagination if needed) or error when counts diverge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
