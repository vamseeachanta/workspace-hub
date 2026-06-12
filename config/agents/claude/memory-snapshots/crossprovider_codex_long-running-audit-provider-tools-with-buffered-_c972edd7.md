---
name: crossprovider codex long-running-audit-provider-tools-with-buffered-
description: Long-running audit/provider tools with buffered output timeout at monitoring intervals
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tooling, observability, feedback]
---

`provider_session_ecosystem_audit.py` takes ~56s but emits zero output until completion; monitoring/timeout loops assume output by 10-30s and kill the process. Long tools should emit progress lines or heartbeat output. Pure-buffered completion-only patterns are operator-hostile and appear stalled to CI/monitoring.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
