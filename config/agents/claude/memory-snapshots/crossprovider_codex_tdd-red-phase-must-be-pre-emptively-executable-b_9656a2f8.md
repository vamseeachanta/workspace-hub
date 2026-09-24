---
name: crossprovider codex tdd-red-phase-must-be-pre-emptively-executable-b
description: TDD red phase must be pre-emptively executable before any edits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, verification, test-planning]
---

Naming a test in the TDD list without specifying its file location, or defining a red-phase command that hasn't been verified to fail before code changes, violates falsifiability. The red phase is the proof you're actually fixing a broken behavior, not an intention. Verify the red command fails independently before entering implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
