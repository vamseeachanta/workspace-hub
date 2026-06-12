---
name: crossprovider hermes cron-health-check-sh-yaml-parser-fixed-via-pytho
description: cron-health-check.sh YAML parser fixed via Python yaml.safe_load() replacement for broken bash parser
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-health, yaml-parsing, monitoring-fix]
---

Commit 0cc3c17e fixed issue #1713: replaced bash string manipulation with `uv run --no-project python` + yaml.safe_load(). Script now parses 27 cron tasks from schedule-tasks.yaml, reports health (24 applicable). Exit code 1 when issues exist (MISSING/STALE/ERROR) = expected behavior, not parse failure. Monitoring is no longer blind.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
