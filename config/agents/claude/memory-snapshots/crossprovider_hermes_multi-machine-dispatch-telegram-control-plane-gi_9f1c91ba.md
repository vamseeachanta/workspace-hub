---
name: crossprovider hermes multi-machine-dispatch-telegram-control-plane-gi
description: Multi-machine dispatch: Telegram control plane, Git sync
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, multi-machine, hermes, telegram]
---

For multi-computer Hermes/agent dispatch (workspace-hub #2720), Telegram Desktop provides notification/control-plane dispatch; Git/GitHub repo state is the authoritative sync layer. Machines pull work from repo, execute, push results; Telegram alerts. Do not use Telegram message history as sync mechanism. Avoids data-consistency hazards of message-history-as-source-of-truth.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
