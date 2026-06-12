---
name: crossprovider hermes parallel-unattended-claude-runs-require-pid-file
description: Parallel unattended Claude runs require PID-file tracking and cron monitoring
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, monitoring, cron-patterns]
---

Use `nohup claude -p "..." > logs/terminal-N.log 2>&1 & echo $! > logs/terminal-N.pid` pattern; monitor completion via cron polling PID files and result markdown files. Follow-up polls may be needed as parallel runs can have stragglers.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
