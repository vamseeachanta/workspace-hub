---
name: crossprovider codex public-surface-verification-must-be-explicit-and
description: Public-surface verification must be explicit and required in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, public-surface-safety, testing]
---

Acceptance criteria claiming public-surface safety must name the full verification command with required flags, not just tool names. Session 6 finding #1: plan claimed public artifacts would be clean but acceptance only ran new validator/tests, omitting the required `--scan-public-path artifacts/ scripts/ tests/` flag from existing validator. This made the claim unverifiable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
