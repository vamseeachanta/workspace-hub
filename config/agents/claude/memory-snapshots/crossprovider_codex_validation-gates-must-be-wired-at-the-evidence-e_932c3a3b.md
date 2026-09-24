---
name: crossprovider codex validation-gates-must-be-wired-at-the-evidence-e
description: Validation gates must be wired at the evidence export boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, validation, fail-safe]
---

New validation logic must be connected at the point where evidence is recorded or serialized, not just defined in isolation. An unwired validation function allows wrong data to bypass it entirely and reach downstream reports, defeating the gate's purpose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
