---
name: crossprovider codex cron-command-key-truncation-at-60-chars-risks-ma
description: Cron command key truncation at 60 chars risks matching failures
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, limitation]
---

cron_apply.py:119-130 truncates fallback catalog command keys to 60 chars when a scripts/*.sh|*.py token is unavailable. Placeholder commands like 'notification-purge' can collide or fail to match against legacy crontab entries, especially when the full command text exceeds 60 chars.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
