---
name: crossprovider codex false-green-liveness-from-stale-cached-artifacts
description: False-green liveness from stale cached artifacts masks missing heartbeat
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [cron-monitoring, false-positives, observability]
---

A publishing-disabled cron can appear healthy if old cached artifacts exist, hiding the underlying missing heartbeat. Separate actual state signal (heartbeat, fresh publish timestamp) from artifact freshness; don't infer liveness from stale-artifact detection alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
