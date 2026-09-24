---
name: crossprovider codex safe-json-string-escaping-in-bash-without-jq
description: Safe JSON string escaping in bash without jq
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, json, shell-safety, no-dependencies]
---

Use sed without external dependencies: `sed 's/\\/\\\\/g; s/"/\\"/g; s/[TAB]/\\t/g'` followed by `tr -d '\000-\037'` to strip control chars. Handles backslash, double-quote, tab, and unprintable characters safely for JSON emission.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
