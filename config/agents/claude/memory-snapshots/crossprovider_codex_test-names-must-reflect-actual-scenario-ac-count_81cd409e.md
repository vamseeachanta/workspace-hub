---
name: crossprovider codex test-names-must-reflect-actual-scenario-ac-count
description: Test names must reflect actual scenario/AC count to prevent silent scope gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-naming, tdd, acceptance-criteria]
---

`test_runbook_covers_four_scenarios` when there are five scenarios is a naming hazard—it lets tests pass while implementation silently misses scope. Test names should exactly match the count or use generic wording like `test_scenarios_completeness`. This applies to any TDD test counting acceptance criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
