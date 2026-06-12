---
name: crossprovider hermes cron-orchestrator-safety-gate-hierarchy-status-a
description: Cron orchestrator safety-gate hierarchy: status → artifact → labels → registry → readiness → dirty-block → lock → disabled-by-default
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orchestration, safety-gates, automation-control, cron]
---

Issue #2740 pattern: require status:plan-approved + .planning/plan-approved/<issue>.md artifact + exactly one machine:* + agent:* labels + registry.yaml validation + readiness evidence + clean/tracked/synced working tree + no-overlap lock + provider execution disabled unless --execute. Each gate fails closed; one failure blocks execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
