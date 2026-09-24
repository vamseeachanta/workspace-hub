---
name: crossprovider gemini markdown-artifact-grep-matching-false-positives-
description: Markdown artifact grep-matching false positives in health monitors
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [monitoring, markdown, regex, false-positive, observability]
---

Health-check monitors using grep-based error pattern matching against `.md` markdown files will false-positive when prose naturally contains keywords like 'error', 'fatal', or 'unreachable'. Plain text regex is unsuitable for markdown content; use JSON status contracts or markdown-aware parsing instead. Broadening patterns like adding 'not found' risks false positives on normal output like '0 files not found'.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
