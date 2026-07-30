---
name: crossprovider codex commit-red-tests-before-production-changes
description: Commit RED tests before production changes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [tdd, incremental-commits, testing, git-workflow]
---

In TDD workflows, commit regression tests as a checkpoint after verifying RED state (failure reproduced) and before implementing the fix; this enables clean bisection and makes the failure-to-fix progression reviewable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
