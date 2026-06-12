---
name: crossprovider gemini safe-jsonl-logging-in-shell-hooks-without-jq-dep
description: Safe JSONL logging in shell hooks without jq dependency
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-hooks, json-escaping, telemetry]
---

Sed pattern `sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g' | tr -d '\000-\037'` escapes JSON strings in one pass for shell hooks. Combines backslash, quote, tab, control-char escaping. Critical when hooks cannot assume external tools.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
