---
name: crossprovider codex single-pass-validation-prevents-tampering-window
description: Single-pass validation prevents tampering windows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, validation, artifact-integrity, parsing]
---

When validating artifacts, operate over the same bytes in one pass: read once, parse once, validate parsed record, digest same bytes. Multiple read-parse cycles create windows where digest and authorization logic operate over different states.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
