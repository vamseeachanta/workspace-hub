---
name: crossprovider hermes test-contract-migration-blockers-require-explici
description: Test contract migration blockers require explicit file updates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-migration, plan-scope, hidden-blocker]
---

When changing brand/structure that existing tests assert (e.g., tests reading root HTML asserting old brand), explicitly list concrete test files in plan's 'Files to Change'. Generic 'update tests' language is insufficient and becomes a hidden blocker at implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
