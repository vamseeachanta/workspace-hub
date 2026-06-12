---
name: crossprovider codex non-interactive-ssh-probes-need-explicit-timeout
description: Non-interactive SSH probes need explicit timeout and batch mode to avoid hanging
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ssh-patterns, reliability, automation]
---

Use ssh -o ConnectTimeout=5 -o BatchMode=yes for remote probes that might hang on network issues; handle empty output gracefully. These flags prevent indefinite waits and let you detect infrastructure problems quickly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
