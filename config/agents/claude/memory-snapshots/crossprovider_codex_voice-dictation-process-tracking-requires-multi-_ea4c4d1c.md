---
name: crossprovider codex voice-dictation-process-tracking-requires-multi-
description: Voice dictation process tracking requires multi-layer validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-management, voice-dictation, safety]
---

Before killing a stale recording process, validate: PID numeric format, matching metadata (UUID), live /proc/<pid>/cmdline containing expected binary and WAV path. This prevents collateral termination of unrelated processes that reuse the same PID.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
