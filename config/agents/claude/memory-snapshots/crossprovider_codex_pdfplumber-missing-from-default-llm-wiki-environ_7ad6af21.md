---
name: crossprovider codex pdfplumber-missing-from-default-llm-wiki-environ
description: pdfplumber missing from default llm-wiki environment
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdfplumber, dependencies, worktree, environment]
---

pdfplumber is not pre-installed in the llm-wiki worktree; install transiently to /tmp only (`pip install --target /tmp/pdfmods pdfplumber`) to avoid repo dependency pollution. Update PYTHONPATH for the session as needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
