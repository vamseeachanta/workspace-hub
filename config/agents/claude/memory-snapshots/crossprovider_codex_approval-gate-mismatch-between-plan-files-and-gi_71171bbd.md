---
name: crossprovider codex approval-gate-mismatch-between-plan-files-and-gi
description: Approval gate mismatch between plan files and GitHub labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, github-workflow, issue-planning]
---

Plan files and GitHub issue labels can diverge on approval status—a plan may still say "not ready" while GitHub shows `status:plan-approved`. Always check both sources; defer execution if approval evidence conflicts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
