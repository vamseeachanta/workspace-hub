---
name: crossprovider codex work-queue-gate-asymmetry-front-gates-enforced-b
description: Work-queue gate asymmetry: front gates enforced, back gates missing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, governance, operational-risk]
---

Planning gates (spec review, resource intelligence) are strictly enforced before work starts. Closure gates (done transition validation, artifact completion, state synchronization) lack equivalent enforcement, causing work items to remain in wrong folders/statuses and breaking telemetry binding to WRK lifecycle.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
