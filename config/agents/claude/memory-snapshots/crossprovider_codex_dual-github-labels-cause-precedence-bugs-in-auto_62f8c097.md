---
name: crossprovider codex dual-github-labels-cause-precedence-bugs-in-auto
description: Dual GitHub labels cause precedence bugs in automation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-labels, automation-bug, state-conflict]
---

When an issue carries both status:plan-review and status:plan-approved simultaneously, readiness builders that check plan-review first will incorrectly treat the issue as not-approved. Verify label precedence order matches intended semantics; resolve conflicts at the source (remove stale plan-review before applying plan-approved).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
