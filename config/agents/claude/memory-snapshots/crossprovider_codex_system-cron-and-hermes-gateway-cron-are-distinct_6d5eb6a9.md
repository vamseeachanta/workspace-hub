---
name: crossprovider codex system-cron-and-hermes-gateway-cron-are-distinct
description: System cron and Hermes Gateway cron are distinct governance planes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron, hermes, ops-governance]
---

System cron (YAML→setup-cron.sh→crontab) and Hermes Gateway cron (`hermes cron list`) are separate scheduler planes with different governance. Do not treat `crontab -l` as canonical Hermes state; use `hermes cron list` for Gateway jobs. Observability logs prove execution; architecture is determined by origin plane.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
