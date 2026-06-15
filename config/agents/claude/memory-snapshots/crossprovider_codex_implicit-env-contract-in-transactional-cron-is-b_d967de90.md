---
name: crossprovider codex implicit-env-contract-in-transactional-cron-is-b
description: Implicit env contract in transactional cron is brittle
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, environment-variables, implicit-contract]
---

The transactional system preserves existing crontab env lines (matching ^[A-Z_]+=) rather than emitting/validating them from the catalog. This creates a dependency on pre-existing crontab state; explicit env handling is needed when transitioning cron management systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
