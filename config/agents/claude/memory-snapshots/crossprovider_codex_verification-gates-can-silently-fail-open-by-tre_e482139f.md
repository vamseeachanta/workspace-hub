---
name: crossprovider codex verification-gates-can-silently-fail-open-by-tre
description: Verification gates can silently fail-open by treating errors as warnings
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [verification, fail-closed, error-handling, gates]
---

Verification gates that convert network/API errors into warnings (e.g., website capability registry treating 404s as non-fatal) allow invalid states to pass. Distinguish between 'check not applicable' (skip) and 'check failed' (error); fail-closed on actual failures, not on transient infrastructure issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
