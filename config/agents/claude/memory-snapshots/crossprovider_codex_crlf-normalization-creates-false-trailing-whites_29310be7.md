---
name: crossprovider codex crlf-normalization-creates-false-trailing-whites
description: CRLF normalization creates false trailing-whitespace warnings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-quirk, line-endings]
---

Normalizing CRLF files causes `git diff --check` to flag every edited line as trailing whitespace, even with no content change. Preserve original line endings to avoid false positives in diff validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
