---
name: crossprovider codex cross-provider-memory-bridge-cron-misconfigured-
description: Cross-provider memory bridge cron misconfigured: missing `--commit` flag
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [memory-system, automation, cron-maintenance, observability]
---

Config specifies `bridge-hermes-claude.sh --commit` but installed crontab runs without it, causing dry-run-only behavior. Contradicts issue #3384 claim of live committing. Schedule-source vs. installed-command drift; requires manual crontab correction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
