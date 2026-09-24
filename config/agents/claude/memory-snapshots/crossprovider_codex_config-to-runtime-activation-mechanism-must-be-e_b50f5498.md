---
name: crossprovider codex config-to-runtime-activation-mechanism-must-be-e
description: Config-to-runtime activation mechanism must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, execution, contracts]
---

If a feature can be enabled via CLI flag, config field, or environment state, the plan must specify which mechanism is authoritative in scheduled execution contexts. Pseudocode and actual scheduled commands must align on how the feature activates, or safeguards/exit-code behavior becomes non-verifiable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
