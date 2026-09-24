---
name: crossprovider codex regex-first-match-only-misses-later-violations-i
description: Regex first-match-only misses later violations in compound commands
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parsing, correctness, edge-cases, regex]
---

Pattern matching only the first occurrence of a write-command (like '>') misses violations that appear later in compound commands or multi-line scripts (e.g., 'benign_cmd && cp src/*/tests/*'). Iteration over all matches or line-by-line parsing is required for correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
