---
name: crossprovider codex plan-approval-requires-explicit-github-issue-lab
description: Plan approval requires explicit GitHub issue labels, not self-declaration
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [plan-gates, approval-workflow, issue-labels]
---

A plan document claiming `status:plan-approved` in its own text does not satisfy approval gates. The GitHub issue MUST carry the `status:plan-approved` label to unblock implementation. Plan-text approval is void without corresponding label evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
