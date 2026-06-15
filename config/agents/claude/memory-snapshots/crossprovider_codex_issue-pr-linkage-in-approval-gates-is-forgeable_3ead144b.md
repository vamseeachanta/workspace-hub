---
name: crossprovider codex issue-pr-linkage-in-approval-gates-is-forgeable
description: Issue-PR linkage in approval gates is forgeable
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, approval-gate, github-automation]
---

Branch names, PR body 'Closes/Refs', and commit trailers allow agents to point unrelated PRs at already-approved issues. Gates need anti-substitution invariants: verify the PR implements the specific approved plan, reject multiple linked issues, reject stale approvals for new PRs, require verification that agent cannot invent the linkage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
