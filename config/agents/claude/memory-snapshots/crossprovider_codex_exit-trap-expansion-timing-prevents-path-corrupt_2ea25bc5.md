---
name: crossprovider codex exit-trap-expansion-timing-prevents-path-corrupt
description: EXIT trap expansion timing prevents path corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, trap-handling, concurrency]
---

Double-quote trap strings to expand variables at definition time, not fire time: trap "rm -rf '$rdir'" EXIT. This bakes the literal path into the trap, safe even after the local var goes out of scope. Avoids race conditions in multi-session environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
