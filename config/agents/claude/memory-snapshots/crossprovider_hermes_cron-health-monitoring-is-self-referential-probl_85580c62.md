---
name: crossprovider hermes cron-health-monitoring-is-self-referential-probl
description: Cron health monitoring is self-referential problem
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monitoring-architecture, system-health, self-reference]
---

When the monitoring job itself fails (cron-health-check broken for 5+ days), it silently masks all other failures. Requires higher-level meta-monitoring or watchdog. Pattern: cron jobs that report health status are not suitable monitors for themselves.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
