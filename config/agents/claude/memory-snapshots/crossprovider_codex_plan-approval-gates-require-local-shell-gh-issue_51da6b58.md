---
name: crossprovider codex plan-approval-gates-require-local-shell-gh-issue
description: Plan-approval gates require local shell `gh issue view`, not API-only
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gates, github, shell, enforcement]
---

The #2802 implementation gate enforces `gh issue view 2802 ... --json state,labels` running in local shell to verify `status:plan-approved`. GitHub connector verification alone does not satisfy the gate; this is a user-required hard gate pattern.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
