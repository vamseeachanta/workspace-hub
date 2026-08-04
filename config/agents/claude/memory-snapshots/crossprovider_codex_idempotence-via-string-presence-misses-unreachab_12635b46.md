---
name: crossprovider codex idempotence-via-string-presence-misses-unreachab
description: Idempotence via string-presence misses unreachable blocks
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [enforcement, installer, shell-scripting]
---

Idempotence checks that test string-presence do not verify reachability. An installer can report success forever after placing blocks below an unconditional exit, preventing auto-repair.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
