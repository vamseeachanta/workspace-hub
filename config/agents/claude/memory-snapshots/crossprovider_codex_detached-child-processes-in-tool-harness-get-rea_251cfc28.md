---
name: crossprovider codex detached-child-processes-in-tool-harness-get-rea
description: Detached child processes in tool harness get reaped on command exit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-lifecycle, batch-work, harness-quirks, environment-specific]
---

When spawning detached batch worker processes via a one-shot command (nohup in a shell script), the children are reaped when that command exits, causing log loss and process death. Move persistent batch work into a dedicated PTY session or use subprocess with lifecycle management to keep workers alive across the tool invocation boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
