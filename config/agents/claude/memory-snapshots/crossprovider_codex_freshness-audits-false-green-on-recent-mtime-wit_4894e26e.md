---
name: crossprovider codex freshness-audits-false-green-on-recent-mtime-wit
description: Freshness audits false-green on recent mtime with missing heartbeat
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [monitoring, liveness-detection, false-positives]
---

When a heartbeat is absent but recent file mtime exists, freshness audit may incorrectly report healthy state. Require explicit heartbeat-present check, not mtime-based freshness alone, to detect stale bridges.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
