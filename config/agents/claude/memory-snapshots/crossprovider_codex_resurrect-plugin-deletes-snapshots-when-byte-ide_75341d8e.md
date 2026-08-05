---
name: crossprovider codex resurrect-plugin-deletes-snapshots-when-byte-ide
description: Resurrect plugin deletes snapshots when byte-identical to prior state
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [tmux, plugin-behavior, file-system]
---

The tmux-resurrect save.sh compares candidate snapshots bytewise with the last saved state (`cmp -s`) and deliberately deletes candidates that are identical. This means consecutive autosaves with unchanged pane layouts produce no new files. Foreground and backgrounded invocations both exhibit this behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
