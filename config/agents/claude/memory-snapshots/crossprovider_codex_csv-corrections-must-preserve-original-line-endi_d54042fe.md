---
name: crossprovider codex csv-corrections-must-preserve-original-line-endi
description: CSV corrections must preserve original line-ending style
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [csv-handling, line-endings, file-integrity]
---

When fixing extraction artifacts (symbol corruption, malformed subscripts), preserve the original CRLF or LF terminator to avoid spurious line-ending diffs. This is especially critical in repos with mixed line-ending files, where naive edits can create large spurious diffs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
