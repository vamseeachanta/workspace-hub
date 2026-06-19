---
name: crossprovider codex fail-open-validation-accepts-undeclared-items
description: Fail-open validation accepts undeclared items
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [validation, testing, security]
---

A validator that only checks for missing required fields but accepts unknown/undeclared fields silently allows scope creep. Validation should be fail-closed: test that unknown labels are caught and rejected, not silently accepted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
