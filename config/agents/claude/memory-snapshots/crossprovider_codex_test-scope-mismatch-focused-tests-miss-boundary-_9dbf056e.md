---
name: crossprovider codex test-scope-mismatch-focused-tests-miss-boundary-
description: Test-scope mismatch: focused tests miss boundary violations in derived-content systems
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [testing, anti-pattern, quality]
---

Tests passing on generated subsections/reports does not verify whole modified surfaces; inherited metadata outside generated markers can silently violate boundaries. Test scope must include both generated markers AND entire modified files to catch all mutations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
