---
name: crossprovider codex cross-issue-plan-dependencies-must-verify-live-i
description: Cross-issue plan dependencies must verify live issue state, not README rows
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [dependencies, issue-blocking, live-state]
---

A plan for #61 assumed blocker #50 was the route/ledger gate, but repo coordination had shifted the responsibility to #51, and #51 itself was still draft/unapproved. README rows and local coordination docs can drift from live GitHub labels/approval state. Plans referencing other issues should verify live labels (`gh issue view`) and approval markers (`.planning/plan-approved/*.md`) before finalizing dependency claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
