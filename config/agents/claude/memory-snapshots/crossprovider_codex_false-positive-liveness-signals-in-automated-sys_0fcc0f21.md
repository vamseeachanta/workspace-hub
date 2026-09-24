---
name: crossprovider codex false-positive-liveness-signals-in-automated-sys
description: False-positive liveness signals in automated systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [system-health, observability, false-positives]
---

Downstream audit reports (e.g., MEMORY-FRESH) can mask broken upstream state (dry-run bridge, missing heartbeat) when liveness verification is not hardened. Use direct heartbeat checks as ground truth rather than downstream audit conclusions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
