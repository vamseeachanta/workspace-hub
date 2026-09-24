---
name: crossprovider codex task-specific-monitoring-requires-co-designed-in
description: Task-specific monitoring requires co-designed instrumentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [observability, monitoring-pattern]
---

cron-health-check.sh scans only generic log error tokens and cannot interpret task-specific evidence formats like 'task=repo-ecosystem-hygiene status=ERROR'. Monitoring systems must be co-designed with the instrumentation format so that task-specific state is visible at collection time, not retrofitted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
