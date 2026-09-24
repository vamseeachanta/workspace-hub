---
name: crossprovider codex safety-test-scope-must-match-all-changed-artifac
description: Safety test scope must match all changed artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-design, scope-coverage]
---

Tests that verify only the primary changed file (e.g., sources/capytaine.md) will miss safety violations introduced in other touched artifacts (concepts, index, log entries). Test scope must comprehensively cover all files modified by the change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
