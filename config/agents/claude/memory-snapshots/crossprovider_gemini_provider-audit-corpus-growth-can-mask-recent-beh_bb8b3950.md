---
name: crossprovider gemini provider-audit-corpus-growth-can-mask-recent-beh
description: Provider-audit corpus growth can mask recent behavior pressure
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [audit, metrics, provider-telemetry]
---

When audit corpus grows faster than recent activity indicates, it creates false-positive drift alerts. Report both recent-window and full-corpus metrics separately; corpus anomalies often reflect historical export or backfill, not current runtime debt.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
