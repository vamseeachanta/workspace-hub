---
name: crossprovider codex voice-dictation-launcher-kills-unrelated-process
description: Voice dictation launcher kills unrelated processes via stale PID
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [safety, tool-quirk, voice-dictation]
---

The codex-dictate launcher uses `kill -0` on a pidfile to detect recorder state but does not validate process identity. A stale pidfile pointing at a reused PID will kill unrelated processes. Fix: validate `/proc/$pid/cmdline` and process start time before killing; fail closed on mismatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
