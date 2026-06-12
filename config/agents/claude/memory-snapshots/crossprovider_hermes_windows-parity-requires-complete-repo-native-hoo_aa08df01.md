---
name: crossprovider hermes windows-parity-requires-complete-repo-native-hoo
description: Windows parity requires complete repo-native hook wiring
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows, hooks, parity, telemetry]
---

Windows Claude Code lacks Hermes-side return sync, so repo-native write-back hooks matter more. session-logger.sh and session-review.sh are not wired in settings.json despite being referenced by emit-session-quality-signals.sh. Windows skill/session artifacts are incomplete without these hooks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
