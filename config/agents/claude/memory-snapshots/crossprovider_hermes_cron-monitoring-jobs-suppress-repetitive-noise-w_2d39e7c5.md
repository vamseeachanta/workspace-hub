---
name: crossprovider hermes cron-monitoring-jobs-suppress-repetitive-noise-w
description: Cron monitoring jobs suppress repetitive noise with [SILENT] response
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-automation, signal-management, workflow-convention]
---

When a scheduled monitoring task (weekly GTM lanes, next-wave status checks) finds no changes from prior run, respond with exactly '[SILENT]' (nothing else, no text) to suppress automatic delivery. Keeps signal-to-noise high for notification subscribers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
