---
name: crossprovider codex dual-parameter-exactly-one-enforcement
description: Dual-parameter exactly-one enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, pydantic, correctness]
---

When a struct accepts either `param_a` or `param_b`, enforce exactly one non-None using Pydantic `@field_validator mode='after'`, not just 'require one'. Silent shadowing when both are present (e.g., lognormal taking mean_log over median) causes correctness hazards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
