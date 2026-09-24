---
name: crossprovider codex gate-enforcement-requires-integration-testing-of
description: Gate enforcement requires integration testing of the gates themselves, not just plan review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, testing, control-plane, workflow]
---

Wrapper guards discovered incomplete gate: execution was allowed on medium/complex items without `plan_reviewed: true` frontmatter. This is a control-plane bug, not a plan oversight. Fixes to gates should include tests that the gate mechanism itself enforces correctly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
