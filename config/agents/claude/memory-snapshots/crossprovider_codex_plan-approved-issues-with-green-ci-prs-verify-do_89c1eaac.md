---
name: crossprovider codex plan-approved-issues-with-green-ci-prs-verify-do
description: Plan-approved issues with green CI PRs: verify, don't restart
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-coordination, pr-workflow, converged-practice]
---

When an issue has status:plan-approved and an open PR with green CI, the next action is verify/update that PR, not start fresh implementation. Check PR branch ancestry against main; branches often lag and need update before merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
