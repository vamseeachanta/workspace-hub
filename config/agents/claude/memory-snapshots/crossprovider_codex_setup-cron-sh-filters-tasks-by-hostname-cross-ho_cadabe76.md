---
name: crossprovider codex setup-cron-sh-filters-tasks-by-hostname-cross-ho
description: setup-cron.sh filters tasks by hostname; cross-host validation needs target execution
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [scheduling, multi-host, validation]
---

setup-cron.sh invokes `hostname -s` to filter applicable tasks. Dry-run validation for cross-alias or multi-host scenarios must run on the actual target host, not a different control host.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
