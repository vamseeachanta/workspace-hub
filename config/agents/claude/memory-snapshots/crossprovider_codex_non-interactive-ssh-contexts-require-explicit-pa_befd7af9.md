---
name: crossprovider codex non-interactive-ssh-contexts-require-explicit-pa
description: Non-interactive SSH contexts require explicit PATH for user-local binaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ssh, cron, path-handling]
---

Cross-machine audits via non-interactive SSH (cron, script invocations) don't source shell rc files, so user-local bin directories (~/.npm-global/bin, ~/.local/bin) are absent from PATH. SSH audit commands must explicitly prepend these paths in the remote shell command, or tools installed locally will appear missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
