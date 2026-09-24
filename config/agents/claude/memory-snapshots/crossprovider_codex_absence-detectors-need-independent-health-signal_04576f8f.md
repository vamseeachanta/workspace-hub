---
name: crossprovider codex absence-detectors-need-independent-health-signal
description: Absence detectors need independent health signals from monitored resources
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, detectors, distributed-systems]
---

Empty telemetry + missing heartbeat should alert as detector-input failure, not report healthy. Detectors cannot use the same gated lease for their own liveness check; requires separate signaling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
