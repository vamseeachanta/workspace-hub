---
name: crossprovider codex stale-installed-cron-state-silently-breaks-bridg
description: Stale installed cron state silently breaks bridge publication
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, deployment, stale-state]
---

The bridge/publication system relies on correct cron installation. If the installed cron schedule drifts from the tracked schedule, publication silently stops even if the bridge code runs correctly. Requires independent scheduler audit vs. tracked-schedule verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
