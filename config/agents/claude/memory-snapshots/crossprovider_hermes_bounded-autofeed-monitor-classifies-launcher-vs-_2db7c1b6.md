---
name: crossprovider hermes bounded-autofeed-monitor-classifies-launcher-vs-
description: Bounded autofeed monitor classifies launcher vs work-result failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monitoring, cron, launcher-classification]
---

Distinguish FAILED_LAUNCHER (script/binary errors before work starts) from COMPLETED_WITH_RESULT (agent produced output) vs STALLED_NO_OUTPUT. Launcher errors like `-budget-usd: command not found`, `claude: command not found`, or `LOGDIR: unbound variable` are infrastructure/script issues, not work completion, and should not be counted as successful agent runs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
