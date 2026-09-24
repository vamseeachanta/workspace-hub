---
name: crossprovider codex fleet-audits-require-separate-status-and-severit
description: Fleet audits require separate status and severity dimensions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit, fleet-management, schema-design]
---

Cross-machine tool audits need two independent concepts: per-machine status (tool present/parseable/missing) and cross-machine drift severity (info/warn/block based on version differences). Conflating them causes ambiguous implementation. Severity is computed only across reachable machines; unreachable machines don't trigger BLOCK conditions. This schema pattern applies broadly to multi-target audits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
