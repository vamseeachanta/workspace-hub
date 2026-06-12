---
name: crossprovider codex hermes-cron-patterns-must-be-codified-as-durable
description: Hermes cron patterns must be codified as durable scheduled tasks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hermes-integration, infrastructure-durability, scheduled-tasks]
---

Emergency infrastructure (e.g., Hermes cron job `d9b2d1c2270d` for renewal automation) created locally but not repo-tracked. Plans must migrate these to durable `config/scheduled-tasks/schedule-tasks.yaml` entries with explicit cron, machine hints, and log paths; otherwise renewal lapses when Hermes session ends.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
