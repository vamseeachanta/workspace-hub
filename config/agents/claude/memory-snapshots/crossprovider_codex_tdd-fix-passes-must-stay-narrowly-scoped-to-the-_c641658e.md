---
name: crossprovider codex tdd-fix-passes-must-stay-narrowly-scoped-to-the-
description: TDD fix passes must stay narrowly scoped to the defect contract
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, scope-management, risk-control]
---

When review surfaces defects in a schema/validation layer, the fix implementation should repair only that contract without expanding into downstream tasks (source-data access, wiki writes, snapshot generation). Narrow scope reduces risk and keeps regressions isolated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
