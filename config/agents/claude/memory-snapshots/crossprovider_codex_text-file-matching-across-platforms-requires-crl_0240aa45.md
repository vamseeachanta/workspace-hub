---
name: crossprovider codex text-file-matching-across-platforms-requires-crl
description: Text file matching across platforms requires CRLF normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-patterns, cross-platform]
---

Markdown/text files may have CRLF line endings from Windows checkouts. Use `tr -d '\r'` before `grep` to ensure consistent matching behavior across platforms and avoid false WARN results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
