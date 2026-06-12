---
name: crossprovider gemini bash-json-escaping-for-jsonl-streams-requires-ta
description: Bash JSON escaping for JSONL streams requires tab and control-char handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash, json, tooling-quirk]
---

When emitting JSONL (newline-delimited JSON) from shell scripts that might receive unvalidated input, use a dedicated escaping function that handles not just quotes and backslashes but also tabs and control characters (sed regex: s/\t/\\t/g, tr -d '\000-\037'). The naive printf approach breaks on tabs in variable values.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
