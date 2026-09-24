---
name: crossprovider gemini vulture-requires-explicit-exit-handling
description: Vulture requires explicit exit handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [vulture, static-analysis, pre-commit]
---

Vulture exits non-zero (exit code 1) by default when dead code is detected. Pre-commit hooks and CI jobs treating it as warn-only must explicitly suppress the exit code with `|| true` or provide a whitelist file via `vulture src/ whitelist.py` to avoid unwanted pipeline failures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
