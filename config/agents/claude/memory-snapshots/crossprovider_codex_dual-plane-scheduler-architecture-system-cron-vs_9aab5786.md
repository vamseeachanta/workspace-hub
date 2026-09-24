---
name: crossprovider codex dual-plane-scheduler-architecture-system-cron-vs
description: Dual-plane scheduler architecture: system-cron vs Hermes Gateway
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, scheduler, workspace-hub, hermes, cron]
---

workspace-hub operates two independent scheduler planes: system-cron (repo-YAML driven via `config/scheduled-tasks/schedule-tasks.yaml` and `setup-cron.sh`) and Hermes Gateway cron (separate managed surface via `hermes cron list`). Migrations between planes require explicit routing contracts; dependencies must be sequenced so contracts precede migrations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
