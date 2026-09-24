---
name: crossprovider codex freshness-signals-produce-false-positives-when-w
description: Freshness signals produce false-positives when weighted unevenly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monitoring, liveness-detection, false-positives]
---

When monitoring liveness via multiple independent indicators (heartbeat, file mtime, bridge status), if heartbeat is absent but recent file mtime exists, the audit returns false-green MEMORY-FRESH. Critical signals like heartbeat must be required, not optional, to prevent masking failure modes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
