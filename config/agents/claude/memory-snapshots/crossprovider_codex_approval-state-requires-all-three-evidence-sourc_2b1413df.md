---
name: crossprovider codex approval-state-requires-all-three-evidence-sourc
description: Approval state requires all three evidence sources
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-drift, execution-readiness, github-workflow]
---

GitHub label state, local approval-marker files (`.planning/plan-approved/*.md`), and plan-index metadata can diverge. Safe execution dispatch needs concurrent verification of all three, not label alone. Approval-labeled issues can remain risky if markers are missing or if a later plan-review pass has staled the index.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
