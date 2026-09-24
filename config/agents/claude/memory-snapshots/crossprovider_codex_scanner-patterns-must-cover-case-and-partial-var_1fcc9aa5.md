---
name: crossprovider codex scanner-patterns-must-cover-case-and-partial-var
description: Scanner patterns must cover case and partial variants
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scanner-safety, pattern-matching, test-coverage, false-positive-risk]
---

Forbidden scanner patterns must catch all case variations and substrings, not just base forms. Pattern `"authority"` alone won't catch `"auth"` or `"authorization"`. Tests must explicitly validate rejection of all variants before merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
