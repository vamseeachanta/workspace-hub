---
name: crossprovider codex path-visibility-installed-binaries-invisible-to-
description: PATH visibility: installed binaries invisible to non-login shells and systemd units
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [systemd, dispatch, automation, environment, path]
---

uv installed at ~/.local/bin but invisible to systemd services and non-interactive shells because ~/.local/bin is added only by .profile/.bashrc login hooks. Dispatch automation runs in those contexts. Contrast: snap-installed binaries on /snap/bin work everywhere. Critical for control-plane automation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
