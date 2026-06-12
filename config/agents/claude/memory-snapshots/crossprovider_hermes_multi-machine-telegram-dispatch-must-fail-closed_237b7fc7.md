---
name: crossprovider hermes multi-machine-telegram-dispatch-must-fail-closed
description: Multi-machine Telegram dispatch must fail closed on gate failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, hermes, safety-gates, dispatch]
---

Dispatch from Telegram across multiple machines requires explicit safety gates: reject on dirty worktrees, unpushed commits, unavailable hosts, unauthorized users, or workflow failures. Telegram is dispatch/notification plane only; GitHub issues/git state/Hermes configs are the canonical sync sources. Redact all secrets from Telegram outputs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
