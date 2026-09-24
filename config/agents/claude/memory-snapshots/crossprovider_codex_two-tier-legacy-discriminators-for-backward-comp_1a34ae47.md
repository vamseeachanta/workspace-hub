---
name: crossprovider codex two-tier-legacy-discriminators-for-backward-comp
description: Two-tier legacy discriminators for backward-compatible gating
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [versioning, backward-compatibility, gating, infrastructure]
---

When enforcing new requirements across versioned items, use multi-tier checks: first filter by ID range (e.g., WRK < 658), then by timestamp cutoff against a named constant (e.g., LOG_GATE_SINCE). This allows grandfathering old work without exceptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
