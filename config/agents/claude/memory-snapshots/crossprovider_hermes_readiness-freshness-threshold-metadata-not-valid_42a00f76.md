---
name: crossprovider hermes readiness-freshness-threshold-metadata-not-valid
description: Readiness freshness threshold metadata not validated at dispatch time
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness, freshness, validation, dispatch-gate]
---

Registry stores `readiness_freshness_threshold_seconds` but implementation doesn't check if readiness reports are older than threshold. Stale data (2+ hours old) can mark a host ready. Dispatch gate must validate report timestamp against config threshold before accepting status.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
