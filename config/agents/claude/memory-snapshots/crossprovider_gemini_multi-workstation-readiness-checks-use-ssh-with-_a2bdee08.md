---
name: crossprovider gemini multi-workstation-readiness-checks-use-ssh-with-
description: Multi-workstation readiness checks use SSH with timeout + stale-report fallback
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [harness, monitoring, distributed-systems]
---

Not all workstations are SSH-accessible; use a short timeout (5s) to avoid hangs, fall back to cached stale-report detection with explicit age thresholds (25h works for nightly cycles) to surface disconnected machines.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
