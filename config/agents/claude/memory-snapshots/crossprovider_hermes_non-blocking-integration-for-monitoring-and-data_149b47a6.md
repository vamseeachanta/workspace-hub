---
name: crossprovider hermes non-blocking-integration-for-monitoring-and-data
description: Non-blocking integration for monitoring and data lookups
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, design, reliability, integration]
---

All monitoring scripts, data intelligence lookups, and briefing integrations should exit 0 even on failure (best-effort, never block session/workflow progression). Allows safe insertion into session start, cron pipelines, and briefing flows without ripple effects.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
