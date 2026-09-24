---
name: crossprovider codex command-key-truncation-at-60-characters-loses-di
description: Command key truncation at 60 characters loses distinctiveness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [identifier-design, command-matching]
---

cron_apply.py truncates fallback catalog command keys to 60 characters. Short placeholder commands like 'notification-purge' lose their full context when truncated, breaking command identification and task matching. Truncation is a last-resort fallback; full raw+rendered keys must be preserved as the canonical source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
