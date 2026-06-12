---
name: crossprovider hermes stall-signatures-in-multi-provider-dispatch
description: Stall signatures in multi-provider dispatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [stall-detection, provider-dispatch, monitoring, recovery]
---

Known non-consuming stalls: Codex logs stuck at 'Reading stdin...', sandbox bwrap failures (loopback RTM_NEWADDR), Gemini 429/capacity exhausted, Claude stream-json without --verbose. Hermes/worker lanes exiting 143 after worktree timeouts. Distinguish stalled lane from slow lane by checking log mtimes + expected output artifacts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
