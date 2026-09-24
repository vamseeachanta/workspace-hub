---
name: crossprovider codex independent-parsing-for-data-extraction-fidelity
description: Independent parsing for data extraction fidelity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-extraction, verification, fidelity, independence]
---

Data extraction reviews are more reliable using independent parsing (e.g., Python against raw .xlsx with `data_only=True`) rather than trusting the extraction script. Newline normalization must handle line-ending artifacts separately from real cell mismatches to avoid masking defects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
