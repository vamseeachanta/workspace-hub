---
name: awk-range-pattern-edge-case-debugging
description: Debugging technique for awk range patterns that collapse when start line matches end pattern
version: 1.0.0
source: auto-extracted
extracted: 2026-04-12
metadata:
  tags: ["awk", "shell-scripting", "debugging", "regex"]
---

# Awk Range Pattern Edge Case Debugging

When using awk range patterns like `/start/,/end/`, be aware that if a line matches BOTH patterns, the range collapses to a single line instead of spanning multiple lines. Debug by: (1) verify the start and end patterns are mutually exclusive, (2) test the regex independently against sample input, (3) if the start line legitimately matches the end pattern, use a helper that skips the header line and captures subsequent indented/nested lines separately rather than relying on range matching.