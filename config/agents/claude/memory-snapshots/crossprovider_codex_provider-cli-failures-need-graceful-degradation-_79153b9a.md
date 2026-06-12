---
name: crossprovider codex provider-cli-failures-need-graceful-degradation-
description: Provider CLI failures need graceful degradation in orchestration
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [orchestration-resilience, provider-apis, error-handling]
---

Quota limits, timeouts, and CLI unavailability are non-fatal in 9-agent ensembles; capture outputs per-agent and continue to synthesis. Marking failed agents as NO_OUTPUT lets synthesis produce partial but useful results instead of hard-failing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
