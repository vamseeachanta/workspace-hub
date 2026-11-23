---
name: batch-syntax-fix-with-regex-line-based-fallback
description: Fix repeated syntax errors across many files using regex, then fall back to line-based parsing when regex fails
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["regex", "batch-fix", "debugging", "python-syntax"]
---

# Batch Syntax Fix with Line-Based Fallback

When regex replacement fails on repeated syntax patterns across 10+ files, write a line-based fixer script that reads/writes line-by-line instead. Test the regex pattern on raw bytes first (`b'...'` notation) to catch invisible whitespace (e.g., `\n\n` vs `\n`). If regex misses edge cases, iterate with simpler patterns or switch to manual line parsing. Verify all files parse cleanly afterward with `ast.parse()` or equivalent before committing.