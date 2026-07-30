---
name: crossprovider codex config-validation-exhaustive-literal-coverage-wi
description: Config validation: exhaustive literal coverage with reverse pairings
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, configuration, coverage]
---

Config literal family coverage must test every required scalar + optional field, including reverse pairings (HTTP fetch + SSH push, not just HTTP + HTTP), absent optional fields, and duplicate-key violations. Parametrize both wrong-value and duplicate cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
