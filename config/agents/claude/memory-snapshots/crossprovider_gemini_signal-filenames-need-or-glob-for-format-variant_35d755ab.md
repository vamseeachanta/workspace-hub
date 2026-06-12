---
name: crossprovider gemini signal-filenames-need-or-glob-for-format-variant
description: Signal filenames need OR-glob for format variants
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [file-patterns, signal-processing, comprehensive-learning]
---

Inconsistent date formatting in JSONL signal files: `${DATE}-*.jsonl` vs `${DATE}.jsonl`. Use `find ... \( -name X -o -name Y \)` to match both patterns. Hooks and scripts may emit either format; hardcoded single-pattern globs silently miss signals.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
