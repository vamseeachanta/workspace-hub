---
name: crossprovider codex upstream-dependencies-override-approval-labels
description: Upstream dependencies override approval labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, dependency-management, issue-execution]
---

If an issue is labeled `status:plan-approved` but comments or plan text declare an explicit upstream gate (e.g., 'wait for #XXXX'), and that upstream issue is still open, implementation must block at a no-code blocker comment. Approval label does not override dependency chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
