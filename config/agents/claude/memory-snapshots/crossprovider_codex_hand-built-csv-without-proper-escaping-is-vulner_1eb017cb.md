---
name: crossprovider codex hand-built-csv-without-proper-escaping-is-vulner
description: Hand-built CSV without proper escaping is vulnerable to field corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [csv, parsing, correctness]
---

Building CSV by string concatenation without escaping commas, quotes, or newlines in field values will eventually produce malformed output. Codex found this in wrk_cost_report.py:80-86. Use `csv.writer` or equivalent library functions that handle escaping automatically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
