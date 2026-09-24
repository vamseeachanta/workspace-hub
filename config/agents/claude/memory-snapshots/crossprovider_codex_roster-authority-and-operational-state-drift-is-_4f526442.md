---
name: crossprovider codex roster-authority-and-operational-state-drift-is-
description: Roster authority and operational state drift is fail-closed architectural debt
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, data-model, canonical-state]
---

When an operational roster (e.g., harness-config.yaml) diverges from its authoritative source (e.g., registry.yaml), that drift is a blocker, not a documentation gap. Authority misalignment must be resolved before promotion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
