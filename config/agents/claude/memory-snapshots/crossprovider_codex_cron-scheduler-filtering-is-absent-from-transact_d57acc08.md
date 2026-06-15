---
name: crossprovider codex cron-scheduler-filtering-is-absent-from-transact
description: Cron scheduler filtering is absent from transactional and audit paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, scheduler-filtering, cross-platform, workspace-hub#3057]
---

Windows catalog tasks currently appear in conflict reports instead of being filtered as non-cron-scheduler. No scheduler field in cron_transaction, cron_apply, or cron-audit. This is a net-new feature for #3057 cutover; transactional cron will include non-Linux tasks unless added.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
