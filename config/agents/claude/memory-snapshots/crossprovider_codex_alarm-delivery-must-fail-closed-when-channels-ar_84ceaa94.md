---
name: crossprovider codex alarm-delivery-must-fail-closed-when-channels-ar
description: Alarm delivery must fail-closed when channels are unreachable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [alarms, fail-closed, silent-failures, delivery]
---

When a notification alarm's purpose is to reach a human, silent delivery failures are indistinguishable from healthy quiet periods. Codex found that swallowed exceptions (missing Telegram token) become silent failures coupled to intentional suppression flags, creating ambiguity. The alarm cannot verify its own liveness without explicit delivery confirmation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
