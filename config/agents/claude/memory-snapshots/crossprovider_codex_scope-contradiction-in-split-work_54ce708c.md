---
name: crossprovider codex scope-contradiction-in-split-work
description: Scope contradiction in split work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, scope-management, work-decomposition]
---

When decomposing work into phases with deferred scope, acceptance criteria and test suites must match the actual scope being delivered — not the full eventual feature. If deferred scope appears in ACs or tests, the plan is internally inconsistent and will fail implementation. Verify: each phase's ACs and test names should reference only in-scope features; use separate WRK IDs for deferred scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
