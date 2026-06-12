---
name: crossprovider codex registry-schema-and-live-operational-evidence-mu
description: Registry schema and live operational evidence must reconcile in readiness probes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [readiness-testing, registry-reconciliation, operational-evidence]
---

When registry declares a capability (e.g., `agent_clis: [claude]`), readiness probes must distinguish declared capability from observed runtime availability (PATH, binaries, auth) and fail when they conflict. Test fixtures must capture actual live-probe outputs with timestamps, not hardcoded assumptions about tool/provider availability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
