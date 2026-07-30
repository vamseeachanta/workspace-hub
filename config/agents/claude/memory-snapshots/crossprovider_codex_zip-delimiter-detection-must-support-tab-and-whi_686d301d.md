---
name: crossprovider codex zip-delimiter-detection-must-support-tab-and-whi
description: ZIP delimiter detection must support tab and whitespace, not just pipe/comma
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [csv-parsing, data-loading, delimiters]
---

PDQ/CSV/TXT files vary by delimiter. Use `pandas.read_csv(sep=None, engine='python')` for auto-detection, or explicitly support pipe, comma, tab, and whitespace. Single-delimiter detection silently produces one-column 'valid' input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
