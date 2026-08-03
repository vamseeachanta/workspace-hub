---
name: crossprovider codex false-green-liveness-in-audits-file-freshness-ma
description: False-green liveness in audits: file freshness masks missing heartbeats
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [monitoring, observability, audit, heartbeat]
---

Audit logic checking only for fresh file presence (e.g., Hermes outputs) reports FRESH even when the bridge heartbeat is absent or stale. Require explicit heartbeat verification, not file-existence proxies, to catch publication breakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
