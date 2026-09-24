---
name: crossprovider codex out-of-band-cron-scheduling-creates-audit-blind-
description: Out-of-band cron scheduling creates audit blind spots
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduling, observability, multi-agent, cron]
---

Hermes-installed crons (e.g., `daily-cleanup` at 23:00) bypass the canonical `schedule-tasks.yaml` → `setup-cron.sh` → live crontab flow, making them invisible to audit and setup tools. Multi-plane schedulers (yaml-declared + out-of-band installed) require explicit reconciliation logic; neither plane alone provides a complete audit surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
