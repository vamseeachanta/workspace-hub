---
name: crossprovider hermes cron-health-check-broken-for-5-days-due-to-path-
description: cron-health-check broken for 5+ days due to PATH missing ~/.local/bin; comprehensive-learning blocked by legal scan violations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, devops, harness-health]
---

Daily cron infrastructure active but cron-health-check has failed since Apr 2 (uv: command not found). Root cause: crontab entry doesn't include $HOME/.local/bin in PATH. comprehensive-learning nightly pipeline accumulates uncommitted local state due to legal scan violations (178→6 violations trend over 3 days). Both need attention: fix PATH in crontab, investigate legal scan false-positives in session logs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
