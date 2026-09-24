---
name: crossprovider codex malformed-input-must-fail-closed-with-error-list
description: Malformed input must fail closed with error lists, never crash
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, error-handling, robustness]
---

When validating user-supplied or external input (configs, evidence objects, references), ensure all failure modes return an error list or denial reason, never raise exceptions. This requires defensive type checks, bounds validation, and explicit error accumulation. Crashes on malformed input hide which inputs are invalid.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
