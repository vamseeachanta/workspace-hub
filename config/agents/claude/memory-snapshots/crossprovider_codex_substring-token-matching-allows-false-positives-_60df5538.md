---
name: crossprovider codex substring-token-matching-allows-false-positives-
description: Substring token matching allows false positives in shell contexts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [shell-token-boundary, security, token-matching]
---

When matching a token (e.g., catalog path) via substring search in cron commands, it will match inside variable assignments and redirections (e.g., `echo --input=.../path.py` or `printf x > .../path.py`). Enforce token boundaries by excluding adjacent word chars, dots, slashes, hyphens (`[\w./-]`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
