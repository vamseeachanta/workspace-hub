---
name: crossprovider codex wrk-state-mirroring-must-warn-not-suppress
description: WRK state mirroring must warn, not suppress
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, error-handling, wrk-traceability]
---

Silently suppressing errors in state-file writes (`2>/dev/null || true`) breaks traceability hooks—invalid WRK IDs or path issues go unnoticed. Emit warnings to stderr instead so failures are visible during development.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
