---
name: crossprovider hermes multi-machine-ssh-probing-needs-timeout-and-safe
description: Multi-machine SSH probing needs timeout and safe shell quoting
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, ssh, cross-platform]
---

When probing machine status across Linux/Windows/macOS via SSH, use explicit timeouts per host (avoid hangs on unreachable machines), and apply `shlex.quote()` to sanitize command strings before passing to shell. Windows Git Bash has different quoting rules than Linux bash.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
