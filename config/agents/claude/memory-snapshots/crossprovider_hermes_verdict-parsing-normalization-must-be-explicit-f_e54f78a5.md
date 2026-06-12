---
name: crossprovider hermes verdict-parsing-normalization-must-be-explicit-f
description: Verdict parsing normalization must be explicit for suffix-bearing forms
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parsing, error-handling, contract-specification]
---

Dedicated verdict lines like `UNAVAILABLE (context truncation — ...)` need explicit normalization rules: whether they map to metadata UNAVAILABLE or parse-failure MAJOR, and how suffix text is preserved. Implicit rules cause producer/consumer misalignment and silent verdict misclassification. Spec'd in #2502 plan-review artifact metadata design.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
