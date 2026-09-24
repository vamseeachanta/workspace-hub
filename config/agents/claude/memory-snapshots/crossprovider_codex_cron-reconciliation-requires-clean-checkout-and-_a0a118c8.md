---
name: crossprovider codex cron-reconciliation-requires-clean-checkout-and-
description: Cron reconciliation requires clean checkout and daemon detection gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-management, operational-safety, concurrent-writes]
---

Transaction-level CAS protects crontab during apply but not against concurrent writers on checkout state, live daemons, or uncommitted files. Reconciliation must gate on main-branch parity, clean git status, and active daemon detection before proceeding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
