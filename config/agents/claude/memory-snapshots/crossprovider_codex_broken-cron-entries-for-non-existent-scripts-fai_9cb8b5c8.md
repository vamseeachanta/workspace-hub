---
name: crossprovider codex broken-cron-entries-for-non-existent-scripts-fai
description: Broken cron entries for non-existent scripts fail silently until cron fires
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron-validation, silent-failures, ops-automation]
---

Crontab entry pointing to `session-analysis-nightly.sh` (missing file) succeeds on install but silently fails when cron runs. Validate script existence and basic shell syntax in cron setup scripts before writing crontab. Use dry-run or test invocation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
