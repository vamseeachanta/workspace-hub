---
name: crossprovider codex non-finite-inputs-nan-inf-silently-create-false-
description: Non-finite inputs (NaN/Inf) silently create false-safe verdicts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [numeric-safety, physics-code, validation-fail-closed]
---

When NaN/Inf propagates through multi-step calculations before reaching a comparison (e.g., NaN > threshold evaluates False), the result can be a false-safe verdict instead of a validation error. In safety-critical code, validate non-finite inputs explicitly at boundaries and fail closed, not open. This spans multiple calculation functions, not just one entry point.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
