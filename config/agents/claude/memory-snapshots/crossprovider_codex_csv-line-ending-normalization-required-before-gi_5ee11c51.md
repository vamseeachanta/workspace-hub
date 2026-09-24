---
name: crossprovider codex csv-line-ending-normalization-required-before-gi
description: CSV line-ending normalization required before git diff --check
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [csv-handling, git-validation, ingest-workflow]
---

Python's CSV writer defaults to CRLF line endings on Windows or when newline parameter is omitted. Every ingest batch encountered this failure: `git diff --check` rejects CRLF in CSVs. Normalize with `unix2dos` or open files with `newline=''` parameter before validation gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
