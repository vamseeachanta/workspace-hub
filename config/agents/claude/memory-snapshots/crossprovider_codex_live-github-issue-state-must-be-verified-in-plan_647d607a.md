---
name: crossprovider codex live-github-issue-state-must-be-verified-in-plan
description: Live GitHub issue state must be verified in plan-readiness gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, gate-ordering, live-state, issue-management]
---

Plans claiming 'removes blocker X' or 'replaces dependency with Y' do not resolve until live `gh issue view` shows the status label changed. Plan-readiness review should verify against GitHub labels and comments, not plan text, because plan text can state intentions without triggering gate transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
