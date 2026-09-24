---
name: crossprovider gemini file-discovery-patterns-need-or-globs-for-multip
description: File discovery patterns need OR-globs for multiple naming conventions
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [find-patterns, data-consolidation, portability]
---

When aggregating from multiple sources, use `find \( -name pattern1 -o -name pattern2 \)` to handle naming variations without missing files. Example: session-analysis.sh needs `find \( -name "${DATE}-*.jsonl" -o -name "${DATE}.jsonl" \)` to catch both consolidated and split formats.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
