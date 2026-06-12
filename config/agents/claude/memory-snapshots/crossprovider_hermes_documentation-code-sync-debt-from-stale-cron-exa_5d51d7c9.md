---
name: crossprovider hermes documentation-code-sync-debt-from-stale-cron-exa
description: Documentation-code sync debt from stale cron examples
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation, drift, cron, legacy, cleanup]
---

Outdated paths and counts in crontab.example, WORKSPACE_HUB_CAPABILITIES_SUMMARY.md, docs/ops/scheduled-tasks.md; setup_cron.sh duplicated in legacy scripts/coordination/context/ location (unused). Causes operator confusion and false leads. Cleanup needed: deprecate old crontab example, sync capability doc to current task inventory, remove legacy setup scripts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
