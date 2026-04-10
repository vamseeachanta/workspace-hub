---
name: batch-syntax-repair-from-injection-errors
description: Detect and fix systematic syntax errors caused by line-injection scripts that split multiline constructs
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["debugging", "syntax-repair", "batch-fix", "python"]
---

# Batch Syntax Repair from Injection Errors

When an automated script inserts lines at fixed positions without parsing context, it often splits multiline imports or statements, causing SyntaxError across multiple files. Use `ast.parse()` to identify all broken files in one pass, then write a regex or line-based fixer that respects continuation blocks (unclosed parentheses, backslashes). Test the fixer on a subset, then apply batch-wide. Verify with full syntax check (`python -m py_compile *.py` or equivalent) before commit.