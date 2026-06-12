---
name: crossprovider codex json-string-escaping-helper-for-untrusted-fields
description: JSON string escaping helper for untrusted fields
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, json, escaping]
---

Single printf + sed chain escapes backslash, double-quote, tabs, strips control chars: printf '%s' "$str" | sed 's/\\/.../g; s/"/\\"/g' | tr -d '\000-\037'. Prevents JSONL injection from environment or command output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
