---
name: crossprovider codex fail-open-defaults-on-missing-enum-values-route-
description: Fail-open defaults on missing enum values route to permissive outcome
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [permission-model, defaults, security-design]
---

When closed enums are defined but code accepts freeform text or omits validation, unknown values default to the most permissive routing (e.g., 'public' instead of 'private'). Always validate presence and enum membership; make missing→fail-closed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
