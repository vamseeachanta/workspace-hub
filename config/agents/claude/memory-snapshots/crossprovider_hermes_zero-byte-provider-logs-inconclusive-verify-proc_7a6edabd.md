---
name: crossprovider hermes zero-byte-provider-logs-inconclusive-verify-proc
description: Zero-byte provider logs inconclusive; verify process liveness + output artifacts instead
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-provider, provider-dispatch, monitoring]
---

A provider-invoked lane showing zero-byte logs does not mean failure or success; check actual process liveness (pgrep), child process activity, and expected output artifacts in results directories. Wrappers running with unchanged logs for hours are not proof of productive throughput.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
