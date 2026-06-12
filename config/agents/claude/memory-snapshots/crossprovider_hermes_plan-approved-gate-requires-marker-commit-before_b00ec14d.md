---
name: crossprovider hermes plan-approved-gate-requires-marker-commit-before
description: Plan-approved gate requires marker commit before implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow-gate, github-issue, approval-discipline]
---

After user approval label, implementation blocks until `.planning/plan-approved/<issue-id>.md` marker is committed. Post-commit hooks can auto-commit markers; prevents implementation drift from stale approval state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
