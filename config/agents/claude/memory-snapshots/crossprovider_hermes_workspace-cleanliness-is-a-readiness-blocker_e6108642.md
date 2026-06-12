---
name: crossprovider hermes workspace-cleanliness-is-a-readiness-blocker
description: Workspace cleanliness is a readiness blocker
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, readiness, git-state, dispatch]
---

Telegram-Hermes readiness fails closed if workspace has uncommitted or untracked changes. Check git status before dispatch readiness assessment; dirty workspace is a hard blocker, not a warning.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
