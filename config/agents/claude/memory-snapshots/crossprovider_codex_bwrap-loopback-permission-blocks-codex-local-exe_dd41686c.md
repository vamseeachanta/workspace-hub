---
name: crossprovider codex bwrap-loopback-permission-blocks-codex-local-exe
description: bwrap loopback permission blocks Codex local execution
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex-sandbox, environment, tooling-quirk]
---

Multiple 2026-04-30 Codex scout sessions failed with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` before any command execution, blocking both shell and Node REPL access to local filesystem. Affects `git status`, `rg`, and file writes; workaround is read-only GitHub connector when available.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
