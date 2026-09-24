---
name: crossprovider codex reconciler-primary-pattern-for-batch-idempotent-
description: Reconciler-primary pattern for batch idempotent operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, github-actions, kanban, idempotency]
---

For operations like kanban board sync, prefer a scheduled reconciler (GitHub Action cron) over per-event webhooks: single batched transaction per run, idempotent, handles missed state automatically, no per-repo hook setup. Pair with idempotency keys (gh:owner/repo#N) and atomic YAML upserts to avoid duplicates across board moves.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
