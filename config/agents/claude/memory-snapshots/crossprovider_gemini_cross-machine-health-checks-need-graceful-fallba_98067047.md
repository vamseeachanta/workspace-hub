---
name: crossprovider gemini cross-machine-health-checks-need-graceful-fallba
description: Cross-machine health checks need graceful fallbacks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [monitoring, resilience, cross-machine]
---

SSH timeout 5s + stale report detection (>25h) + degraded exit code (2) enable partial health visibility. compare-harness-state.sh tries SSH, falls back to stale-report age check, continues. One machine down doesn't fail the whole check. Best-effort (|| true) in cron.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
