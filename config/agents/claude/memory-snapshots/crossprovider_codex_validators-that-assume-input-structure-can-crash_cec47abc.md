---
name: crossprovider codex validators-that-assume-input-structure-can-crash
description: Validators that assume input structure can crash instead of gracefully deny
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [robustness, validation, error-handling]
---

Validators that assume well-formed input after recording validation errors can throw (AttributeError/KeyError) on malformed inputs instead of returning controlled DENY state. This creates inconsistent failure modes depending on where malformation occurs. Structure validation or safe nested accessors must precede policy checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
