---
name: crossprovider codex orchestrator-logging-must-use-wrk-id-timestamp-f
description: Orchestrator logging must use WRK-ID + timestamp for cross-provider traceability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [logging, orchestration, traceability]
---

Per-provider log paths (claude/, codex/, gemini/) make cross-agent trace reconstruction hard; standardize on logs/orchestrator/<provider>/<WRK-ID>-<timestamp>.log so workflow steps can be correlated across agents and providers in single query.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
