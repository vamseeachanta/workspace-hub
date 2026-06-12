---
name: crossprovider gemini bulk-string-replacement-breaks-command-v-availab
description: Bulk string replacement breaks command -v availability checks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, uv, tool-migration, cross-platform, pattern-matching]
---

Replacing `python3` with `uv run --no-project python` via bulk sed breaks scripts using `command -v python3` for availability detection, since `command -v` only matches the binary name. Three patterns require distinct fixes: availability checks (binary name only), inline execution (wrap command), shebangs (`env -S`), and jq fallback chains (binary name in logic only).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
