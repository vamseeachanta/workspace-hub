---
name: crossprovider codex path-matrices-require-exhaustive-classification-
description: Path matrices require exhaustive classification via git ls-files tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, validation, completeness]
---

Representative test coverage leaves gaps where unclassified tracked files cause silent passes or self-blocks. Tests must enumerate every tracked text/code path and verify it's included with rationale or explicitly excluded.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
