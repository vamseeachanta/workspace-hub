---
name: crossprovider hermes hermes-telegram-dispatch-readiness-blockers
description: Hermes Telegram dispatch readiness blockers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, telegram, readiness-check, deployment]
---

Dispatch fails when: TELEGRAM_ALLOWED_USERS or TELEGRAM_BOT_TOKEN env vars missing, workspace has uncommitted/untracked changes, host-local readiness evidence absent, path/config drift. config/workstations/registry.yaml is canonical registry; Windows/macOS dispatch disabled pending planning/review/approval. Use readiness scripts to pre-verify before execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
