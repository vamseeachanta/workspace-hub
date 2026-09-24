---
name: crossprovider codex liveness-via-absence-needs-explicit-freshness-bo
description: Liveness via absence needs explicit freshness boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [liveness-detection, monitoring, timeouts]
---

Heartbeat-as-liveness where absence of recent signal indicates a down host requires explicit timeout constants and freshness checks. Plain absence reading as success is a silent-failure trap; need structured freshness semantics with timeout and boundary conditions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
