---
name: crossprovider codex drift-verdict-excludes-unreachable-machines-from
description: Drift verdict excludes unreachable machines from calculation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [architecture, multi-machine, reliability]
---

In parity audits, unreachable machines are excluded from drift severity computation; they never contribute to BLOCK verdicts. This pattern is load-bearing for split-fleet scenarios where some machines are temporarily offline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
