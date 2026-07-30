---
name: crossprovider codex composite-health-checks-with-incomplete-coverage
description: Composite health checks with incomplete coverage produce false-green signals
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [observability, audit-design]
---

A memory-system audit reported 'FRESH' despite a missing bridge heartbeat because fresh Hermes files masked the absence. When aggregating health signals from multiple components, incomplete coverage creates misleading results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
