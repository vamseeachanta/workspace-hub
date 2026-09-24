---
name: crossprovider codex remote-availability-checks-should-degrade-gracef
description: Remote availability checks should degrade gracefully, not block
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [resilience, remote-operations, error-handling]
---

SSH and remote resource checks should handle unavailability with `|| true` and log skip/warn, not fail hard. Remote transience is normal; graceful skipping preserves overall system robustness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
