---
name: crossprovider hermes cron-log-scan-self-poisoning-from-health-check-o
description: Cron log scan self-poisoning from health check output
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, monitoring, gotcha]
---

Scanning full append-only cron logs picks up the health-check script's own [ERROR] rows, creating false positives on every run. Fix: scan only recent log tail (e.g., last 100 lines) with case-sensitive/anchored ERROR matching to avoid matching unrelated strings like "Client Error".

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
