---
name: crossprovider codex non-interactive-shell-path-divergence-breaks-too
description: Non-interactive shell PATH divergence breaks tool audits
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron, ssh, path-resolution, audit-reliability]
---

Scripts run in cron/SSH environments have different PATH than interactive shells. Tools installed to ~/.npm-global/bin or managed by nvm/uv may not resolve when audited via non-interactive SSH, creating false-missing signals. Audits targeting deployment parity must use explicit PATH prefixes (e.g., `ssh host 'PATH=$HOME/.npm-global/bin:$PATH tool --version'`) to match cron reality, not interactive shell.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
