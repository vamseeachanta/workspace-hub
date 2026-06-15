---
name: crossprovider codex api-shape-changes-require-auditing-all-callers-n
description: API shape changes require auditing all callers, not just the definition
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [refactoring, testing, api-stability]
---

Changing a function's return type (e.g., from a list to a tuple) introduces regressions in callers that weren't updated. A grep for the function name plus manual inspection of each call site is required before merging API refactors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
