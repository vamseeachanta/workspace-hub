---
name: crossprovider codex backward-compatible-api-keyword-only-parameter-e
description: Backward-compatible API keyword-only parameter extension
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [api-design, backward-compat]
---

When adding metadata parameters to an existing positional API, preserve slots exactly and introduce new parameters as keyword-only (after `*`) with sensible defaults. Example: `calculate(card, inclination_deg, tubing_id, *, load_datum='net_pump_load', ...)` keeps `calculate(card, 30, 2.441)` working.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
