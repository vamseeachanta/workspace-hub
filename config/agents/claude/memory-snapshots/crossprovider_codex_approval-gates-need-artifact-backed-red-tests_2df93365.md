---
name: crossprovider codex approval-gates-need-artifact-backed-red-tests
description: Approval gates need artifact-backed RED tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, tdd, approval-gates, testing]
---

Plans that require approval before implementation are not executable unless coupled with RED tests checking for an approval marker file (e.g., `.planning/plan-approved/N.md`). Prose-only approval gates are invisible to the implementation harness. Found repeatedly across llm-wiki #760-#763 reviews: plans stated approval gates but had no test that would fail when the marker was absent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
