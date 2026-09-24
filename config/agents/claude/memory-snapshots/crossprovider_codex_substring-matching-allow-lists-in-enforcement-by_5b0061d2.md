---
name: crossprovider codex substring-matching-allow-lists-in-enforcement-by
description: Substring-matching allow-lists in enforcement bypass checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-gates, allow-list-design, false-negatives]
---

Allow-lists that suppress enforcement based on substrings (e.g., 'any line containing model-registry') are too permissive — comments and unrelated text bypass checks. Use anchored patterns or explicit documented-reference requirements instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
