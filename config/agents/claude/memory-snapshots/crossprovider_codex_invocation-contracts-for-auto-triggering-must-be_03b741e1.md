---
name: crossprovider codex invocation-contracts-for-auto-triggering-must-be
description: Invocation contracts for auto-triggering must be explicit in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, orchestration, specification]
---

Plans that define auto-triggering behavior (e.g., 'auto-checkpoint at 85% context usage') are incomplete without specifying the concrete caller, event, or signal that fires the trigger. Abstract triggers like 'when context is low' are not executable; plans must name the source that will pass `--usage-pct` or equivalent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
