---
name: crossprovider codex detached-background-workers-from-one-shot-comman
description: Detached background workers from one-shot commands are reaped immediately
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [background-processes, process-lifecycle, detached-children]
---

Using `nohup` or backgrounding from a one-shot shell command does not prevent child reaping when the parent exits. Persistent PTY or session manager required to keep detached workers alive. Symptom: logs stay empty despite worker launching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
