---
name: crossprovider codex false-green-audit-liveness-when-fresh-subsystem-
description: False-green audit liveness when fresh subsystem output masks missing heartbeat
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [auditing, observability, false-positives, multi-component]
---

Memory-freshness audit reported healthy status despite the bridge running in dry-run with no heartbeat. Fresh output from one subsystem (Hermes) masked the missing publication signal in another (bridge). Multi-component audits must verify each signal independently, not rely on composite freshness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
