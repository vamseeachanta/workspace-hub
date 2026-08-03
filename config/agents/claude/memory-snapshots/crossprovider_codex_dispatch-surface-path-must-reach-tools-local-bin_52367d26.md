---
name: crossprovider codex dispatch-surface-path-must-reach-tools-local-bin
description: Dispatch surface PATH must reach tools; ~/.local/bin insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [dispatch, shell-execution, path-visibility]
---

Tools in `~/.local/bin` are invisible to systemd user units and non-interactive shells. Dispatch surfaces require tools on the system PATH (e.g. `/snap/bin`) or installed system-wide, not in user-local locations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
