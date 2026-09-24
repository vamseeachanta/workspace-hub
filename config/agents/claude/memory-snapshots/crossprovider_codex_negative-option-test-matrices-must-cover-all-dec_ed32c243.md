---
name: crossprovider codex negative-option-test-matrices-must-cover-all-dec
description: Negative-option test matrices must cover all declared prefixes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, completeness, options]
---

When a plan specifies multiple option negations, the test matrix must exhaustively cover all of them, not just one. Omission masks implementation failures of untested prefixes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
