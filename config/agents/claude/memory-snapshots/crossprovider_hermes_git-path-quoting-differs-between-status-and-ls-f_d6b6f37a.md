---
name: crossprovider hermes git-path-quoting-differs-between-status-and-ls-f
description: Git path quoting differs between status and ls-files
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, path-parsing]
---

Git `status` output uses C-quoted paths with octal escapes (e.g., `'path\ with\ space'`); `git ls-files` uses raw UTF-8. Checker must decode C-quotes and octal escapes for status, but not for ls-files. Verify `shlex.split` handles octal correctly or use explicit unquoting.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
