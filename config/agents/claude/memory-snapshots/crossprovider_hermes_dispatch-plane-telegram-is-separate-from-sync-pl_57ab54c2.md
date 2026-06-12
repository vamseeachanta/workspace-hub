---
name: crossprovider hermes dispatch-plane-telegram-is-separate-from-sync-pl
description: Dispatch plane (Telegram) is separate from sync plane (GitHub/git)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, dispatch, synchronization, planes]
---

Telegram carries notifications and dispatch commands only. Canonical sync authority remains GitHub issues/comments/labels, git commits, and repo state. Never treat Telegram as source of truth for work state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
