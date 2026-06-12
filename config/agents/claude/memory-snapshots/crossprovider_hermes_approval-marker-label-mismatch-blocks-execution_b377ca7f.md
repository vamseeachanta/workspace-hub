---
name: crossprovider hermes approval-marker-label-mismatch-blocks-execution
description: Approval marker/label mismatch blocks execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, execution-readiness, github-workflow]
---

GitHub `status:plan-approved` label and local `.planning/plan-approved/<issue>.md` marker must BOTH exist for execution to proceed. Absence of either creates a silent gate. Sessions found this pattern blocking workspace-hub#2656, worldenergydata#394, assethold#49, aceengineer-website#13, aceengineer-strategy#19.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
