---
name: crossprovider codex csv-line-ending-round-trip-preservation
description: CSV line-ending round-trip preservation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [csv, file-handling, line-endings, data-integrity]
---

csv.reader() and text mode strip trailing line terminators; naive rewrites normalize mixed CRLF/LF to LF, creating phantom diffs on unchanged rows. Capture per-row terminators on read (raw bytes split on \n, infer \r\n vs \n), store as metadata, and replay on write.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
