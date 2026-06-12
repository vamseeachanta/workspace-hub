---
name: crossprovider gemini regex-error-patterns-false-positive-on-markdown-
description: Regex error patterns false-positive on markdown prose
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cron-health, regex-fragility, monitoring]
---

Cron health monitors parsing `.md` artifact files with `ERROR_PATTERNS` regex (e.g., `grep 'fatal'`) will false-positive on english text containing words like 'fatal' or 'failed'. Markdown tasks need structured status (JSON) or separate prose/status sections to avoid misclassification.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
