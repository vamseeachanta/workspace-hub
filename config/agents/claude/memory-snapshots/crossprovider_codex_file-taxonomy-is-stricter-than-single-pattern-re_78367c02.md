---
name: crossprovider codex file-taxonomy-is-stricter-than-single-pattern-re
description: File taxonomy is stricter than single-pattern regexes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-taxonomy, test-placement, validation-accuracy]
---

Tests should not live under `src/` at all; they belong under `tests/<domain>/`. A regex like `src/.*/tests/` is weaker than the actual taxonomy rule and misses patterns like `src/.../test_*.py` or `src/.../conftest.py`. Taxonomy enforcement should reference the actual rule, not weaker approximations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
