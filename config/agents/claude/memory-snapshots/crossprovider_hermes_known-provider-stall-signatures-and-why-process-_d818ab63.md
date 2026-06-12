---
name: crossprovider hermes known-provider-stall-signatures-and-why-process-
description: Known provider stall signatures and why process-only monitoring fails
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-debugging, codex, gemini, monitoring]
---

Codex hangs on stdin read without </dev/null; bwrap loopback fails with RTM_NEWADDR error; Gemini returns 429 RESOURCE_EXHAUSTED under capacity; Claude requires --verbose for stream-json; worktree timeouts exit 143. Process count is insufficient—monitor log mtimes and file sizes across snapshots instead. Stale logs with live PID indicates the process is blocked, not progressing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
