---
name: crossprovider codex csv-writer-line-ending-conflicts-with-git-diff-c
description: CSV writer line-ending conflicts with git diff --check
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [csv, git, line-endings, llm-wiki, verification]
---

Python's csv.DictWriter defaults to system line endings (CRLF on some configs); generated CSVs must be normalized to LF before `git diff --check` or the verification gate fails. Normalize with `dos2unix` or Python's newline='' parameter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
