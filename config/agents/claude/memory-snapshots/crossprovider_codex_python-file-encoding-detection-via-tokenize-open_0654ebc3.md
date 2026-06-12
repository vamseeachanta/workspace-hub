---
name: crossprovider codex python-file-encoding-detection-via-tokenize-open
description: Python file encoding detection via tokenize.open()
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [python, encoding, robustness]
---

For robust scanning of Python files with PEP 263 source encoding declarations (e.g., `# -*- coding: utf-8 -*-`), use `tokenize.open(filename)` instead of hardcoded UTF-8 `read_text()`. This handles non-UTF-8 source files correctly without silent data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
