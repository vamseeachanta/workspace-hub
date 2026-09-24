---
name: crossprovider gemini thin-bash-wrapper-python-entrypoint-for-cron-scr
description: Thin bash wrapper + Python entrypoint for cron scripts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, cron, scripting-patterns]
---

Use a bash wrapper (`#!/usr/bin/env bash; exec uv run --no-project python ...`) to invoke Python entrypoint. Preserves shebang composability while leveraging Python's superior yaml/json/subprocess handling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
