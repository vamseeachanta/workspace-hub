---
name: crossprovider codex licensed-standards-values-must-use-fail-closed-g
description: Licensed standards values must use fail-closed getters, never hardcoded
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, compliance, architecture, engineering]
---

Store licensed standard values (codes, guidelines, thresholds) in private wiki with fail-closed getter functions; never hardcode in public code. This enables verification of source authority, centralizes compliance auditing, and allows tests to prove getters fail safely when the wiki is unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
