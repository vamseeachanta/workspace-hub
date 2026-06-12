---
name: crossprovider hermes hermes-memories-don-t-auto-port-across-machines
description: Hermes memories don't auto-port across machines
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, portability, memory]
---

~2KB of live Hermes memories (MEMORY.md, USER.md) stay machine-local (~/.hermes/); no git tracking, no automated restore. Only distilled YAML snapshots travel via git. New machines lose live memory state; must manually recreate or rsync. Gap: no backward-sync from Claude → Hermes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
