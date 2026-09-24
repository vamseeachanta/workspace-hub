---
name: crossprovider gemini regex-log-parsing-produces-false-positives-prefe
description: Regex log parsing produces false positives; prefer structured formats
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell-safety, log-analysis, data-extraction]
---

Scanning session logs with raw regex patterns (e.g., `python3 ` for runtime violations) matches conversational mentions, commit messages, and output text—not actual violations. WRK-691 reviews flagged this repeatedly. Instead, parse structured formats (JSONL) or use field-targeted tools (jq, Python) to extract specific command/commit data.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
