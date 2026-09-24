---
name: crossprovider codex cross-reference-validation-is-missing-in-artifac
description: Cross-reference validation is missing in artifact-deletion plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [regression, deletion, validation]
---

Plans that delete/move artifacts rarely include explicit regression tests to verify zero dangling references. This should be wired into acceptance criteria and test strategy, not left to manual verification or skipped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
