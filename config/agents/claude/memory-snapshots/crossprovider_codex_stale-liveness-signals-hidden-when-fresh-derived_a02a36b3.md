---
name: crossprovider codex stale-liveness-signals-hidden-when-fresh-derived
description: Stale liveness signals hidden when fresh derived artifacts cache older heartbeats
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [monitoring, observability, architecture]
---

Bridge heartbeat missing (dry-run mode) but cached/derived artifacts exist → monitoring shows FRESH status masking the broken heartbeat. Heartbeat verification must be independent from data-freshness checks; sentinel files and explicit timestamps disambiguate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
