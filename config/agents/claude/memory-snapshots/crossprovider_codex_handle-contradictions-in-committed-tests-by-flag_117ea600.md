---
name: crossprovider codex handle-contradictions-in-committed-tests-by-flag
description: Handle contradictions in committed tests by flagging for user authorization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, governance, integrity]
---

When committed test suite contains mutually exclusive assertions (e.g., one test requires a field, another rejects cases containing it), identify the exact contradiction, report which design choices it blocks, and request authorization to resolve. Do not weaken test assertions or reorder tests to hide the contradiction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
