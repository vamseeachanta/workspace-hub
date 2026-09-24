---
name: crossprovider codex verifier-token-parsing-for-glob-pattern-rejectio
description: Verifier token parsing for glob pattern rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, linting, regression-testing]
---

Linting verifiers must parse command token lists, not just check for immediate position. E.g., rejecting `flake8 .` by position alone misses appended targets like `flake8 src/ . file.py`; parse all tokens to catch patterns wherever they appear.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
