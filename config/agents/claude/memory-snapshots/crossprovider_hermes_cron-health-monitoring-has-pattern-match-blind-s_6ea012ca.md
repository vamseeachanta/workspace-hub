---
name: crossprovider hermes cron-health-monitoring-has-pattern-match-blind-s
description: Cron health monitoring has pattern-match blind spots
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, monitoring, false-positive]
---

Cron-health scans only for ERROR pattern in logs and checks log naming (cron-*.log), missing errors like 'uv not found' that don't match ERROR and scripts that write to different paths (e.g., parity-review-*.md). Results in silent false-positive OK verdicts. Need explicit error-class list and log-path mapping.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
