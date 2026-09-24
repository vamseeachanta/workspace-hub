---
name: crossprovider codex mixing-structured-and-unstructured-output-in-one
description: Mixing structured and unstructured output in one stream breaks downstream tooling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [csv, output-format, downstream-compatibility]
---

Appending human-readable footers to CSV rows corrupts the output for downstream parsers. Codex found this in wrk_cost_report.py: `format_cost_table(..., csv_mode=True)` emitted CSV rows then a parenthetical line, making stdout invalid CSV. Route annotations to stderr or a separate channel, or keep stdout pure structured data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
