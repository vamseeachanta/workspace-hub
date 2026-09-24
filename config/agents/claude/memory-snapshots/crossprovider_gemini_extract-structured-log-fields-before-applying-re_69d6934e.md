---
name: crossprovider gemini extract-structured-log-fields-before-applying-re
description: Extract structured log fields before applying regex validation to avoid false positives
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [log-parsing, regex-validation, false-positives]
---

Raw regex on JSONL or text logs flags incidental text matches (strings in outputs, read files, thoughts). Parse structured fields first (jq for JSONL), validate extracted content. Prevents text mentions being incorrectly classified as violations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
