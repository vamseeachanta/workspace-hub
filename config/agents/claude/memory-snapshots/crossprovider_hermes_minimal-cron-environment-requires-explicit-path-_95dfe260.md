---
name: crossprovider hermes minimal-cron-environment-requires-explicit-path-
description: Minimal cron environment requires explicit PATH for helper invocation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, environment, shell, debugging]
---

Cron jobs run with minimal environment. Scripts invoking `uv`, `git`, `npm`, or other tools need explicit `PATH=/usr/local/bin:/usr/bin:...` setup in the command or script prologue, not shell initialization. Missing PATH causes silent 'command not found' failures in logs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
