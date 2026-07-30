---
name: crossprovider codex memory-audit-false-green-from-fresh-artifacts-ma
description: Memory audit false-green from fresh artifacts masking heartbeat
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [memory-system, audit-design, monitoring]
---

Fresh Hermes files can mask missing bridge heartbeat/liveness signal, causing audit to report MEMORY-FRESH when subsystem is actually down. Audit logic must check heartbeat independently of artifact freshness; artifact age alone is insufficient signal.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
