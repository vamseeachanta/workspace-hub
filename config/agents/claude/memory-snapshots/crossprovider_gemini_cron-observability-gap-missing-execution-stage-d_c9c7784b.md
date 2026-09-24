---
name: crossprovider gemini cron-observability-gap-missing-execution-stage-d
description: Cron observability gap: missing execution-stage diagnostics
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cron, observability, diagnostics, test-isolation, instrumentation]
---

Current cron health monitors classify tasks as MISSING, STALE, or OK, but cannot distinguish whether a task is absent from crontab, present but not firing, failing before log creation, or failing during script execution. Hermetic wrapper tests with stubbed external calls and mocked `sourced` helper libraries are needed to isolate failure stages and provide actionable diagnostics.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
