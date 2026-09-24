---
name: crossprovider codex revision-bound-approval-gates-in-issue-comments
description: Revision-bound approval gates in issue comments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, scope-binding, issue-execution]
---

Plan approvals can be bound to a specific commit SHA (e.g., 'approved for plan/issue-XXXX at 7cc1c0b1a'). Current worktree must contain that commit and plan files must match the approved revision; if drift occurs, implementation must block with blocker comment rather than proceeding against a changed plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
