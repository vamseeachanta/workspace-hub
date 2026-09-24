---
name: crossprovider gemini json-jsonl-safety-in-bash-sed-based-string-escap
description: JSON/JSONL safety in bash: sed-based string escaping avoids injection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, security, json, string-escaping]
---

Create `_json_str()` helper using sed to escape backslash, double-quote, and tab; strip control chars with `tr -d '\000-\037'`. Use when emitting JSONL or JSON from shell scripts with untrusted values. Prevents injection and corruption of downstream parsers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
