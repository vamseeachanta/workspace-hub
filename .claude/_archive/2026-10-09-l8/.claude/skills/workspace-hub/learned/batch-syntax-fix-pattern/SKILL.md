---
name: batch-syntax-fix-pattern
description: Identify and repair cascading import/syntax errors across multiple files using regex-based line-scanning and verification
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["refactoring", "debugging", "regex", "multi-file-fixes"]
---

# Batch Syntax Error Fix Pattern

When a code migration (e.g., print→logger) breaks syntax in multiple files with the same root cause, write a line-based fixer script instead of manual edits. Use `ast.parse()` or similar to verify all 995+ source files parse after the fix, then commit atomically. Key: test the regex on a single file first, then batch-apply and validate in one pass to catch cascading breakage patterns (e.g., blank lines in mid-import statements) that manual spot-fixes miss.