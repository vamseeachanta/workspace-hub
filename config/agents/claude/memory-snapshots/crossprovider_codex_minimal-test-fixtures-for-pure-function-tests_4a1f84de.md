---
name: crossprovider codex minimal-test-fixtures-for-pure-function-tests
description: Minimal test fixtures for pure-function tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, test-fixtures, tdd, minimal-setup]
---

When testing pure functions (e.g., `check_agent_log_gate()`), fixtures need only directory structure and empty marker files; omit actual content unless the test specifically validates file parsing. Reduces fixture complexity and maintenance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
