---
name: crossprovider hermes hermes-cross-machine-config-transferable-vs-mach
description: Hermes cross-machine config: transferable vs machine-specific split
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, cross-machine-config, sync-infrastructure, schedule-tasks]
---

~/.hermes structure: repo-synced (skills/, SOUL.md, config.yaml minus credentials) vs machine-local (auth.json, .env, state.db, sessions/, memories/). Existing sync: scripts/_core/sync-agent-configs.sh (JSON-merge preserving overrides), scripts/cron/harness-update.sh (daily). Current gap: harness-update in schedule-tasks.yaml runs only on ace-linux-1; ace-linux-2 receives repository-sync + memory-backup only. Recommendation: add harness-update to ace-linux-2 task schedule.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
