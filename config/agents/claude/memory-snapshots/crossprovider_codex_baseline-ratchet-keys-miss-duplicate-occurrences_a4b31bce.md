---
name: crossprovider codex baseline-ratchet-keys-miss-duplicate-occurrences
description: Baseline ratchet keys miss duplicate occurrences
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-gates, ratchet-design, regression-masking]
---

Enforcement ratchets keyed on (path, token) pairs allow duplicate new occurrences of the same literal in the same file to pass undetected. Use occurrence-level or line-level tracking instead, or require exact (path, line, token) triples.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
