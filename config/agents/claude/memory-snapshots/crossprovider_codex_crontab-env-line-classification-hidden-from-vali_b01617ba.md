---
name: crossprovider codex crontab-env-line-classification-hidden-from-vali
description: Crontab env-line classification hidden from validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, testing-gap, validation, observability]
---

`cron_transaction.py` classifies `^[A-Z_]+=` lines as `ignore` (non-managed) and preserves them outside the managed block, but `cron_apply.py --json` output omits the rendered crontab text and env contract, making this preservation invisible to dry-run validation. Operators cannot confirm env-vars are defined before cutover.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
