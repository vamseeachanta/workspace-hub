---
name: crossprovider codex python-review-commands-require-pythondontwriteby
description: Python review commands require PYTHONDONTWRITEBYTECODE=1 to avoid staged-scope pollution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, python, hygiene, staging]
---

Python validators, tests, and scanners create `__pycache__` directories unless explicitly prevented. When reviewing staged content, prefix all Python commands with `PYTHONDONTWRITEBYTECODE=1` or remove caches before final status, so review residue doesn't contaminate the staged-diff scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
