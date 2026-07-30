---
name: crossprovider codex fail-closed-validation-for-external-source-integ
description: Fail-closed validation for external source integration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [data-integration, fail-closed-patterns, validation]
---

When integrating external data into strict contracts (e.g., RSU-0077 tension-to-rotate with source dicts), validation must verify numeric consistency between governing and case values, validate all mappings exist, and default to `missing-inputs` on any inconsistency. Partial success silently breaking downstream (e.g., mismatched tension values) is worse than explicit failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
