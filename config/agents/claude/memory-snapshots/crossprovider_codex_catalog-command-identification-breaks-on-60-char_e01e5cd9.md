---
name: crossprovider codex catalog-command-identification-breaks-on-60-char
description: Catalog command identification breaks on 60-character truncation for placeholder commands
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, command-identity, deduplication, workspace-hub#3057]
---

cron_apply.py:119-130 prefers scripts/*.sh|*.py tokens for command identity; fallback truncates catalog keys to 60 chars. Placeholder commands like notification-purge that don't match a script token get broken identities, blocking deduplication and audit trails. Needs full raw+rendered fallback keys.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
