---
name: batch-regex-fix-import-syntax
description: Detect and fix mid-import blank-line syntax breaks across multiple files using line-based regex
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["refactoring", "batch-fix", "regex", "imports", "python"]
---

# Batch Regex Fix for Mid-Import Syntax Breaks

When migrations introduce blank lines within multi-line imports (e.g., `import (\n\n` instead of `import (\n`), use a line-based sed/awk fixer instead of single-pass regex. First identify the pattern across all files with grep, then apply a simple line-aware regex that matches `^import (` followed by a blank line, replacing with `import (` on the next non-blank line. Test parse afterward with `python -m py_compile` or equivalent to verify all 995+ files are clean before committing.