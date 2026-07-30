---
name: crossprovider codex api-parameter-additions-must-preserve-positional
description: API parameter additions must preserve positional argument order
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [api-design, backwards-compat]
---

Adding new required keyword-only parameters (e.g., `load_datum`) while retaining existing positional arguments in original order prevents breaking existing callers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
