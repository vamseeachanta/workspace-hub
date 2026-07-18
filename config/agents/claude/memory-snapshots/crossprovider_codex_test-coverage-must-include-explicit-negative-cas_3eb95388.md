---
name: crossprovider codex test-coverage-must-include-explicit-negative-cas
description: Test coverage must include explicit negative cases for identity references
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [testing, schema-validation, identity-references]
---

Presence/absence tests for identity-based fields allow fail-open behavior even when intent is fail-closed. Negative test cases must exercise malformed, empty, or mistyped identities to verify actual rejection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
