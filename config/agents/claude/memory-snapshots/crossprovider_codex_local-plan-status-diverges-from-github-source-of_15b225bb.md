---
name: crossprovider codex local-plan-status-diverges-from-github-source-of
description: Local plan status diverges from GitHub source-of-truth
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, github, sync, workflow]
---

docs/plans/README.md local status field drifts from actual GitHub issue labels (e.g., README says 'plan-review', GitHub shows 'status:plan-approved'). Always check `gh issue view` for authoritative approval state before assuming a plan needs new authorization or proceeding with implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
