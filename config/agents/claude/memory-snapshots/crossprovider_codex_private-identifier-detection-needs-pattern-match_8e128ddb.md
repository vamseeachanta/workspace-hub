---
name: crossprovider codex private-identifier-detection-needs-pattern-match
description: Private identifier detection needs pattern matching, not hardcoded labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, privacy, pattern-matching]
---

String-matching only hardcoded label strings (client-id, confidentiality-tag) misses common identifier patterns: email addresses, phone numbers, bank account formats, social-security-number structures, proprietary vocabulary. Use regex patterns or heuristics; maintain allow/deny lists to catch unlabeled sensitive content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
