---
name: crossprovider codex stale-report-detection-via-generated-at-age-thre
description: Stale-report detection via generated_at + age threshold is more robust than SSH-only health checks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [remote-monitoring, state-freshness, health-checks]
---

Instead of just testing SSH connectivity, check report generated_at timestamp against age threshold (e.g., >25h old). Detects both SSH failure and process-not-running. Graceful degradation: flag explicitly when SSH works but report is stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
