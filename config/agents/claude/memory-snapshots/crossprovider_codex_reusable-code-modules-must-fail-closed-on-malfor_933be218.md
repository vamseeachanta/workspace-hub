---
name: crossprovider codex reusable-code-modules-must-fail-closed-on-malfor
description: Reusable code modules must fail closed on malformed input
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [code-review, correctness, validation]
---

A scorer that accepts any truthy `met` value (not strict boolean validation) fails unsafe on malformed JSON/data. If a wrapper adds stricter validation, both the wrapper and bare scorer must be tested—callers may use the reusable path without the wrapper.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
