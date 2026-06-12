---
name: crossprovider codex entry-point-fallback-tests-must-use-valid-entry-
description: Entry-point fallback tests must use valid entry paths with missing optionals
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, control-flow, test-design]
---

Tests for 'missing component → fallback warning' fail when the entry code exits before reaching fallback (e.g., missing stage contract exits before checking micro-skill). Tests should use valid entry paths with valid-but-missing optional components, not invalid inputs that exit early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
