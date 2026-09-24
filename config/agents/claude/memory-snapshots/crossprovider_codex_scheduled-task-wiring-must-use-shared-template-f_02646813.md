---
name: crossprovider codex scheduled-task-wiring-must-use-shared-template-f
description: Scheduled task wiring must use shared template for all OSes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduling, cron, task-scheduler, template-generation]
---

Per-machine scheduling (Linux cron and Windows Task Scheduler) must be generated from one shared template/config; separate implementations cause drift and missed sync points.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
